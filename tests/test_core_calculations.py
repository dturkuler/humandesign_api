import pytest
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from humandesign import features as hd

def test_hd_features_snapshot():
    """
    Regression test to ensure hd_features logic remains consistent during refactor.
    Using a canonical birth time: 1987-01-20 04:30:00 UTC+1 (Europe/Berlin)
    """
    # 1987, 1, 20, 4, 30, 0, offset=1.0
    # Note: hd_features typically expects local time and offset
    timestamp = (1987, 1, 20, 4, 30, 0, 1.0)
    
    # calc_single_hd_features returns a tuple
    # We ignore report, channel_meaning, day_chart_only as they are False by default/usage
    result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    
    # Unpack for clarity (based on api.py usage)
    energy_type = result[0]
    authority = result[1]
    inc_cross = result[2]
    profile = result[4]
    definition = result[5]
    gates = result[6]
    active_chakras = result[7]
    channels = result[8]
    
    # SNAPSHOT ASSERTIONS
    assert energy_type == "Generator"
    assert authority == "SL"
    assert profile == (4, 6)
    assert inc_cross == "((60, 56), (50, 3))-RAC"
    assert definition == 3
    assert active_chakras == {'RT', 'SL', 'TT', 'SN', 'AA', 'HT'}
    
    # Check Channels structure
    assert isinstance(channels, dict)
    assert set(channels.keys()) == {'label', 'planets', 'gate', 'ch_gate', 'gate_chakra', 'ch_gate_chakra', 'ch_gate_label', 'gate_label'}
    # Basic check that we have channels (based on output 'prs' etc)
    assert len(channels['gate']) > 0
    
    # Check Gates structure
    assert isinstance(gates, dict)
    expected_gate_keys = ['label', 'planets', 'lon', 'gate', 'line', 'color', 'tone', 'base', 'ch_gate']
    assert list(gates.keys()) == expected_gate_keys
