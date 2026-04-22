from unittest.mock import MagicMock, mock_open, patch

from app.services.system_service import systemService


def test_stats_with_thermal_file():
    with (
        patch("builtins.open", mock_open(read_data="45000\n")),
        patch("psutil.cpu_percent", return_value=25.5),
        patch("psutil.virtual_memory") as mock_mem,
    ):
        mock_mem.return_value.percent = 62.3
        stats = systemService.get_syst_stats()

    assert stats["cpu_temp"] == 45.0
    assert stats["cpu_usage"] == 25.5
    assert stats["ram_usage"] == 62.3
    assert stats["status"] == "Online"


def test_stats_without_thermal_file_returns_na():
    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        patch("psutil.cpu_percent", return_value=10.0),
        patch("psutil.virtual_memory") as mock_mem,
    ):
        mock_mem.return_value.percent = 40.0
        stats = systemService.get_syst_stats()

    assert stats["cpu_temp"] == "N/A"
    assert stats["status"] == "Online"


def test_stats_permission_error_on_thermal():
    with (
        patch("builtins.open", side_effect=PermissionError),
        patch("psutil.cpu_percent", return_value=5.0),
        patch("psutil.virtual_memory") as mock_mem,
    ):
        mock_mem.return_value.percent = 20.0
        stats = systemService.get_syst_stats()

    assert stats["cpu_temp"] == "N/A"


def test_stats_cpu_usage_within_valid_range():
    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        patch("psutil.cpu_percent", return_value=0.0),
        patch("psutil.virtual_memory") as mock_mem,
    ):
        mock_mem.return_value.percent = 0.0
        stats = systemService.get_syst_stats()

    assert 0.0 <= stats["cpu_usage"] <= 100.0
    assert 0.0 <= stats["ram_usage"] <= 100.0


def test_stats_temperature_rounded_to_one_decimal():
    with (
        patch("builtins.open", mock_open(read_data="52345\n")),
        patch("psutil.cpu_percent", return_value=0.0),
        patch("psutil.virtual_memory") as mock_mem,
    ):
        mock_mem.return_value.percent = 0.0
        stats = systemService.get_syst_stats()

    assert stats["cpu_temp"] == 52.3
