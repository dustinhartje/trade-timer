// ind_filters ranges are half-open: [low, high) — low is included, high is not.
window.TIMER_CONFIG =
{
  "strategies": [
    {
      "name": "IRA Bounce",
      "type": "long",
      "offset": -10,
      "ema_key": "e1h9ema",
      "ind_filter_labels": [
        "default: rcr_refresh_cycle_20260808-1786224944-84102b9e_long"
      ],
      "valid_hours": {
        "Sunday": [],
        "Monday": [
          10,
          13
        ],
        "Tuesday": [
          10,
          14
        ],
        "Wednesday": [
          9,
          10
        ],
        "Thursday": [
          9,
          10,
          11,
          14
        ],
        "Friday": [
          10,
          15
        ],
        "Saturday": []
      }
    },
    {
      "name": "IRA Reject",
      "type": "short",
      "offset": 40,
      "ema_key": "e1h9ema",
      "ind_filter_labels": [
        "default: rcr_refresh_cycle_20260808-1786224944-84102b9e_short"
      ],
      "valid_hours": {
        "Sunday": [],
        "Monday": [
          11,
          12
        ],
        "Tuesday": [
          9,
          14,
          15
        ],
        "Wednesday": [
          11,
          14,
          15
        ],
        "Thursday": [
          9,
          10,
          11,
          14
        ],
        "Friday": [
          9,
          11,
          13,
          15
        ],
        "Saturday": []
      }
    }
  ],
  "ind_filters": [
    {
      "label": "default: rcr_refresh_cycle_20260808-1786224944-84102b9e_long",
      "ind_id": "ES_eth_e1d_RSI_close_p14_swilder",
      "mode": "exclude",
      "trade_direction": "long",
      "ranges": [
        [
          25,
          40
        ],
        [
          45,
          50
        ],
        [
          65,
          70
        ],
        [
          75,
          80
        ]
      ]
    },
    {
      "label": "default: rcr_refresh_cycle_20260808-1786224944-84102b9e_short",
      "ind_id": "ES_eth_e1d_RSI_close_p14_swilder",
      "mode": "exclude",
      "trade_direction": "short",
      "ranges": [
        [
          55,
          60
        ]
      ]
    }
  ]
};
