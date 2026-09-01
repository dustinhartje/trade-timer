#!/usr/bin/env python3
"""Play the Trade Timer buzzer for configured Eastern-time trade hours."""

import json
import os
import re
import signal
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / 'config.js'
BUZZER_PATH = ROOT / 'tickingbuzzer_28sec.mp3'
END_OF_DAY_PATH = ROOT / 'end_of_day_closing_28sec.mp3'
TRADE_SUBMIT_PATH = ROOT / 'trade_submit_bippity_bleep.wav'
POLL_SECONDS = 0.25
CONFIG_CHECK_SECONDS = 1

os.environ['TZ'] = 'America/New_York'
time.tzset()

running = True


def log(message, stream=sys.stdout):
    print(f'{datetime.now():%Y-%m-%d %H:%M:%S} ET {message}', file=stream, flush=True)


def stop(_signal, _frame):
    global running
    running = False


def load_hours():
    source = CONFIG_PATH.read_text(encoding='utf-8')
    match = re.search(r'window\.TIMER_CONFIG\s*=\s*(\{.*\})\s*;?\s*$', source, re.DOTALL)
    if not match:
        raise ValueError('config.js does not contain a window.TIMER_CONFIG JSON assignment')

    config = json.loads(match.group(1))
    strategies = config.get('strategies')
    if not isinstance(strategies, list):
        raise ValueError('config.js is missing a strategies list')

    return [
        {'name': strategy.get('name', 'Unnamed strategy'), 'hours': strategy.get('valid_hours', {})}
        for strategy in strategies
        if isinstance(strategy, dict)
    ]


def playback_reasons(strategies, now):
    weekday = now.strftime('%A')
    current_hour = now.hour
    next_hour = current_hour + 1
    reasons = []
    for strategy in strategies:
        valid_hours = strategy['hours'].get(weekday, [])
        if current_hour == 9 and now.minute == 24 and current_hour in valid_hours:
            reasons.append(f"before {strategy['name']} 9:30 AM market open")
        elif current_hour in valid_hours:
            reasons.append(f"end of {strategy['name']} {current_hour % 12 or 12}:00 {'AM' if current_hour < 12 else 'PM'} tradeable hour")
        if now.minute != 24 and next_hour != 9 and next_hour in valid_hours:
            reasons.append(f"before {strategy['name']} {next_hour % 12 or 12}:00 {'AM' if next_hour < 12 else 'PM'} tradeable hour")
    return reasons


def has_valid_trade_hour(strategies, now):
    weekday = now.strftime('%A')
    return any(now.hour in strategy['hours'].get(weekday, []) for strategy in strategies)


def playback_event(strategies, now):
    weekday = now.strftime('%A')
    if (weekday not in ('Saturday', 'Sunday') and now.hour == 15 and now.minute == 54
        and 30 <= now.second < 34):
        return 'end-of-day', ['end of day: close all trades']
    if (((now.hour == 9 and now.minute == 29)
        or (now.hour != 9 and now.minute == 0)) and 55 <= now.second < 59):
        if has_valid_trade_hour(strategies, now):
            return 'trade-submit', ['valid trade hour: submit the trade if it has not been invalidated']
    if (((now.hour == 9 and now.minute == 24) or now.minute == 59)
        and 30 <= now.second < 34):
        reasons = playback_reasons(strategies, now)
        if reasons:
            return 'boundary', reasons
    return None, []


def next_playback(strategies, now):
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    for offset in range(8 * 24 + 1):
        candidate_hour = hour_start + timedelta(hours=offset)
        candidates = [
            candidate_hour.replace(minute=0, second=55),
            candidate_hour.replace(minute=59, second=30),
        ]
        if candidate_hour.hour == 9:
            candidates.extend([
                candidate_hour.replace(minute=24, second=30),
                candidate_hour.replace(minute=29, second=55),
            ])
        if candidate_hour.hour == 15:
            candidates.append(candidate_hour.replace(minute=54, second=30))

        for candidate in sorted(candidates):
            if candidate <= now:
                continue
            event_kind, reasons = playback_event(strategies, candidate)
            if event_kind:
                return candidate, reasons
    return None, []


def log_next_playback(strategies):
    scheduled_at, reasons = next_playback(strategies, datetime.now())
    if scheduled_at:
        log(f'Next playback: {scheduled_at:%Y-%m-%d %I:%M:%S %p} ET; ' + '; '.join(reasons))
    else:
        log('No playback is scheduled in the next eight days.')


def play_sound(sound_path):
    subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'error', str(sound_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def main():
    for sound_path in (BUZZER_PATH, END_OF_DAY_PATH, TRADE_SUBMIT_PATH):
        if not sound_path.is_file():
            log(f'Sound file not found: {sound_path}', sys.stderr)
            return 1
    if not shutil.which('ffplay'):
        log('ffplay is required. Install it with: sudo apt install ffmpeg', sys.stderr)
        return 1

    hours_by_strategy = []
    config_mtime = None
    last_config_check = 0.0
    played_event_id = None

    log(f'Trade Timer buzzer watching {CONFIG_PATH}')
    while running:
        monotonic_now = time.monotonic()
        if monotonic_now - last_config_check >= CONFIG_CHECK_SECONDS:
            last_config_check = monotonic_now
            try:
                current_mtime = CONFIG_PATH.stat().st_mtime_ns
                if current_mtime != config_mtime:
                    hours_by_strategy = load_hours()
                    config_mtime = current_mtime
                    log('Loaded configuration.')
                    log_next_playback(hours_by_strategy)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                log(f'Cannot load config: {error}', sys.stderr)

        now = datetime.now()
        event_kind, reasons = playback_event(hours_by_strategy, now.replace(microsecond=0))
        event_id = f'{now:%Y-%m-%d %H:%M}-{event_kind}' if event_kind else None
        if event_kind and played_event_id != event_id:
            sound_path = {
                'boundary': BUZZER_PATH,
                'end-of-day': END_OF_DAY_PATH,
                'trade-submit': TRADE_SUBMIT_PATH,
            }[event_kind]
            play_sound(sound_path)
            played_event_id = event_id
            log('Played ' + event_kind + '; ' + '; '.join(reasons))
            log_next_playback(hours_by_strategy)
        elif not event_kind:
            played_event_id = None

        time.sleep(POLL_SECONDS)

    return 0


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    sys.exit(main())