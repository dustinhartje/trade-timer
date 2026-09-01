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
        if current_hour == 9 and now.minute == 29 and current_hour in valid_hours:
            reasons.append(f"before {strategy['name']} 9:30 AM market open")
        elif current_hour in valid_hours:
            reasons.append(f"end of {strategy['name']} {current_hour % 12 or 12}:00 {'AM' if current_hour < 12 else 'PM'} tradeable hour")
        if now.minute != 29 and next_hour != 9 and next_hour in valid_hours:
            reasons.append(f"before {strategy['name']} {next_hour % 12 or 12}:00 {'AM' if next_hour < 12 else 'PM'} tradeable hour")
    return reasons


def next_playback(strategies, now):
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    for offset in range(8 * 24 + 1):
        candidate_hour = hour_start + timedelta(hours=offset)
        candidates = [candidate_hour.replace(minute=59, second=30)]
        if candidate_hour.hour == 9:
            candidates.insert(0, candidate_hour.replace(minute=29, second=30))

        for candidate in candidates:
            if candidate <= now:
                continue
            reasons = playback_reasons(strategies, candidate)
            if reasons:
                return candidate, reasons
    return None, []


def log_next_playback(strategies):
    scheduled_at, reasons = next_playback(strategies, datetime.now())
    if scheduled_at:
        log(f'Next playback: {scheduled_at:%Y-%m-%d %I:%M:%S %p} ET; ' + '; '.join(reasons))
    else:
        log('No playback is scheduled in the next eight days.')


def play_buzzer():
    subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'error', str(BUZZER_PATH)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def main():
    if not BUZZER_PATH.is_file():
        log(f'Buzzer file not found: {BUZZER_PATH}', sys.stderr)
        return 1
    if not shutil.which('ffplay'):
        log('ffplay is required. Install it with: sudo apt install ffmpeg', sys.stderr)
        return 1

    hours_by_strategy = []
    config_mtime = None
    last_config_check = 0.0
    buzzed_hour = None

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
        trigger_hour = now.strftime('%Y-%m-%d %H')
        in_buzzer_window = (
            (now.minute == 59 or (now.hour == 9 and now.minute == 29))
            and 30 <= now.second < 34
        )
        reasons = playback_reasons(hours_by_strategy, now)
        if in_buzzer_window and buzzed_hour != trigger_hour and reasons:
            play_buzzer()
            buzzed_hour = trigger_hour
            log('Played buzzer; ' + '; '.join(reasons))
            log_next_playback(hours_by_strategy)
        elif not in_buzzer_window:
            buzzed_hour = None

        time.sleep(POLL_SECONDS)

    return 0


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    sys.exit(main())