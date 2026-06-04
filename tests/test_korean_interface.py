import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_declares_korea_only_design():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "한국 사용 환경 전용" in readme
    assert "한국어 우선" in readme
    assert "현대자동차·기아·제네시스" in readme


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
    assert strings["entity"]["button"]["lock_vehicle"]["name"] == "차량 잠금"
    assert strings["entity"]["button"]["unlock_vehicle"]["name"] == "차량 잠금 해제"
    assert strings["entity"]["button"]["start_engine"]["name"] == "원격 시동 켜기"
    assert strings["entity"]["button"]["stop_engine"]["name"] == "원격 시동 끄기"
    assert strings["entity"]["button"]["turn_hvac_on"]["name"] == "공조 켜기"
    assert strings["entity"]["button"]["turn_hvac_off"]["name"] == "공조 끄기"
    assert ko == strings
