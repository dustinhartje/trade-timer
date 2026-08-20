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
          9,
          13,
          15
        ],
        "Tuesday": [
          10,
          11,
          12,
          14
        ],
        "Wednesday": [
          9,
          10,
          12,
          14,
          15
        ],
        "Thursday": [
          10,
          11,
          12
        ],
        "Friday": [
          11
        ],
        "Saturday": []
      }
    },
    {
      "name": "IRA Reject",
      "type": "short",
      "offset": -20,
      "ema_key": "e1h9ema",
      "ind_filter_labels": [
        "default: rcr_refresh_cycle_20260808-1786224944-84102b9e_short"
      ],
      "valid_hours": {
        "Sunday": [],
        "Monday": [
          9,
          12,
          13,
          14,
          15
        ],
        "Tuesday": [
          9,
          11,
          14,
          15
        ],
        "Wednesday": [
          9,
          10,
          12
        ],
        "Thursday": [
          9,
          10,
          11,
          12,
          13,
          14
        ],
        "Friday": [
          14
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
          39.99
        ],
        [
          45,
          49.99
        ],
        [
          65,
          69.99
        ],
        [
          75,
          79.99
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
          59.99
        ]
      ]
    }
  ]
};
