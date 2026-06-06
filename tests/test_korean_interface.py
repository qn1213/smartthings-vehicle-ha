import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_is_distribution_focused_and_korean_first():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "현대자동차·기아·제네시스" in readme
    assert "## HACS 설치" in readme
    assert "## 최초 설정" in readme
    assert "## 주요 기능" in readme
    assert "## 개발" not in readme
    assert "설계 원칙" not in readme


def test_home_assistant_visible_strings_are_korean_first():
    manifest = json.loads(
        (ROOT / "custom_components/smartthings_vehicle/manifest.json").read_text(
            encoding="utf-8"
        )
    )
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    strings = json.loads(
        (ROOT / "custom_components/smartthings_vehicle/strings.json").read_text(
            encoding="utf-8"
        )
    )
    ko = json.loads(
        (ROOT / "custom_components/smartthings_vehicle/translations/ko.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["name"] == "스마트싱스 차량"
    assert hacs["name"] == "스마트싱스 차량"
    assert strings["config"]["step"]["user"]["title"] == "스마트싱스 차량"
    assert strings["entity"]["sensor"]["range_km"]["name"] == "주행 가능 거리"
    assert strings["entity"]["sensor"]["command_state"]["name"] == "명령 상태"
    assert set(strings["entity"]["button"]) == {"refresh", "ping_vehicle"}
    assert strings["entity"]["lock"]["door_lock"]["name"] == "차량 잠금"
    assert set(strings["entity"]["switch"]) == {"hvac", "hvac_defog"}
    assert strings["entity"]["switch"]["hvac"]["name"] == "공조"
    assert strings["entity"]["switch"]["hvac_defog"]["name"] == "앞유리 김서림 제거"
    assert set(strings["entity"]["select"]) == {"hvac_defog", "hvac_ignition_duration"}
    assert strings["entity"]["select"]["hvac_ignition_duration"]["name"] == "공조 작동 시간"
    assert strings["entity"]["climate"]["hvac_climate"]["name"] == "에어컨"
    assert ko == strings
