import pytest
from cybsuite.cyberdb import pm_reporters


def test_json_report_empty(new_cyberdb):
    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check empty lists
    assert data["controls"] == []
    assert data["observations"] == []

    # Check summary structure
    summary = data["summary"]
    assert summary["total_control_definitions"] == 0
    assert summary["total_control_occurrences"] == 0
    assert summary["total_observations_definitions"] == 0
    assert summary["total_observations_occurrences"] == 0

    # Check severity stats structure
    severity_stats = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }

    # Check severity stats values
    assert summary["controls_definitions_by_severity"] == severity_stats
    assert summary["observations_definitions_by_severity"] == severity_stats
    assert summary["observations_occurrences_by_severity"] == severity_stats


def test_json_report_one_ko_control(new_cyberdb):
    # Create one control definition with one KO occurrence (this will appear as both control and observation)
    c_weak_password = new_cyberdb.feed(
        "control_definition",
        name="weak_password",
        severity="medium",
    )[0]

    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="certain",
        control_definition=c_weak_password,
        details={
            "password": "azerty",
        },
    )

    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check control list has one item
    assert len(data["controls"]) == 1
    control = data["controls"][0]

    # Check control definition
    assert control["name"] == "weak_password"
    assert control["max_severity"] == "medium"
    assert control["confidence"] == "certain"
    assert control["status"] == "ko"
    assert control["total_status_ok"] == 0
    assert control["total_status_ko"] == 1
    assert control["total_occurrences"] == 1
    assert set(control["all_keys"]) == {"password"}  # Check all_keys

    # Check control occurrence
    assert len(control["occurrences"]) == 1
    occurrence = control["occurrences"][0]
    assert occurrence["status"] == "ko"
    assert occurrence["severity"] == "medium"
    assert occurrence["confidence"] == "certain"
    assert occurrence["details"] == {
        "password": "azerty",
    }

    # Check observation list has one item (the same control with status=ko)
    assert len(data["observations"]) == 1
    observation = data["observations"][0]

    # Check observation (which is just the same control)
    assert observation["name"] == "weak_password"
    assert observation["max_severity"] == "medium"
    assert observation["confidence"] == "certain"
    assert observation["total_occurrences"] == 1
    assert set(observation["all_keys"]) == {"password"}  # Check all_keys

    # Check observation occurrence
    assert len(observation["occurrences"]) == 1
    occurrence = observation["occurrences"][0]
    assert occurrence["severity"] == "medium"
    assert occurrence["confidence"] == "certain"
    assert occurrence["details"] == {
        "password": "azerty",
    }

    # Check summary
    summary = data["summary"]
    assert summary["total_control_definitions"] == 1
    assert summary["total_control_occurrences"] == 1
    assert (
        summary["total_observations_definitions"] == 1
    )  # The KO control appears as observation
    assert (
        summary["total_observations_occurrences"] == 1
    )  # The KO occurrence appears as observation

    # Check severity stats
    assert summary["controls_definitions_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 1,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_definitions_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 1,  # The KO control appears here
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_occurrences_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 1,  # The KO occurrence appears here
        "low": 0,
        "info": 0,
        "unknown": 0,
    }


def test_json_report_one_ok_control(new_cyberdb):
    # Create one control definition with one OK occurrence (this will only appear as control)
    c_strong_password = new_cyberdb.feed(
        "control_definition",
        name="strong_password",
        severity="medium",
    )[0]

    new_cyberdb.feed(
        "control",
        status="ok",
        severity="medium",
        confidence="certain",
        control_definition=c_strong_password,
        details={
            "password": "StrongP@ssw0rd123",
        },
    )

    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check control list has one item
    assert len(data["controls"]) == 1
    control = data["controls"][0]

    # Check control definition
    assert control["name"] == "strong_password"
    assert control["max_severity"] == "medium"
    assert control["confidence"] == "certain"
    assert control["status"] == "ok"
    assert control["total_status_ok"] == 1
    assert control["total_status_ko"] == 0
    assert control["total_occurrences"] == 1
    assert control["all_keys"] == ["password"]  # Check all_keys

    # Check control occurrence
    assert len(control["occurrences"]) == 1
    occurrence = control["occurrences"][0]
    assert occurrence["status"] == "ok"
    assert occurrence["severity"] == "medium"
    assert occurrence["confidence"] == "certain"
    assert occurrence["details"] == {
        "password": "StrongP@ssw0rd123",
    }

    # Check observation list is empty (OK controls don't appear as observations)
    assert len(data["observations"]) == 0

    # Check summary
    summary = data["summary"]
    assert summary["total_control_definitions"] == 1
    assert summary["total_control_occurrences"] == 1
    assert (
        summary["total_observations_definitions"] == 0
    )  # OK controls don't appear as observations
    assert (
        summary["total_observations_occurrences"] == 0
    )  # OK occurrences don't appear as observations

    # Check severity stats
    assert summary["controls_definitions_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 1,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_definitions_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 0,  # OK controls don't appear here
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_occurrences_by_severity"] == {
        "critical": 0,
        "high": 0,
        "medium": 0,  # OK occurrences don't appear here
        "low": 0,
        "info": 0,
        "unknown": 0,
    }


def test_json_report_multiple_controls(new_cyberdb):
    # Create weak_password control definition with 2 OK occurrences
    c_weak_password = new_cyberdb.feed(
        "control_definition",
        name="weak_password",
        severity="medium",
    )[0]

    new_cyberdb.feed(
        "control",
        status="ok",
        severity="medium",
        confidence="certain",
        control_definition=c_weak_password,
        details={
            "password": "StrongP@ssw0rd123",
        },
    )
    new_cyberdb.feed(
        "control",
        status="ok",
        severity="medium",
        confidence="certain",
        control_definition=c_weak_password,
        details={
            "password": "StrongP@ssw0rd456",
        },
    )

    # Create ldap_anonymous control definition with 5 occurrences (2 KO, 3 OK)
    c_ldap = new_cyberdb.feed(
        "control_definition",
        name="ldap_anonymous",
        severity="high",
    )[0]

    # Add 2 KO occurrences
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="high",
        confidence="certain",
        control_definition=c_ldap,
        details={
            "ip": "192.168.1.100",
            "port": 389,
        },
    )
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="high",
        confidence="certain",
        control_definition=c_ldap,
        details={
            "ip": "192.168.1.101",
            "port": 389,
        },
    )
    # Add 3 OK occurrences
    new_cyberdb.feed(
        "control",
        status="ok",
        severity="high",
        confidence="certain",
        control_definition=c_ldap,
        details={
            "ip": "192.168.1.102",
            "port": 389,
        },
    )
    new_cyberdb.feed(
        "control",
        status="ok",
        severity="high",
        confidence="certain",
        control_definition=c_ldap,
        details={
            "ip": "192.168.1.103",
            "port": 389,
        },
    )
    new_cyberdb.feed(
        "control",
        status="ok",
        severity="high",
        confidence="certain",
        control_definition=c_ldap,
        details={
            "ip": "192.168.1.104",
            "port": 389,
        },
    )

    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check control list has two items
    assert len(data["controls"]) == 2

    # Check weak_password control
    weak_password = [e for e in data["controls"] if e["name"] == "weak_password"][0]
    assert weak_password["name"] == "weak_password"
    assert weak_password["max_severity"] == "medium"
    assert weak_password["confidence"] == "certain"
    assert weak_password["status"] == "ok"
    assert weak_password["total_status_ok"] == 2
    assert weak_password["total_status_ko"] == 0
    assert weak_password["total_occurrences"] == 2
    assert set(weak_password["all_keys"]) == {"password"}  # Check all_keys

    # Check weak_password occurrences
    assert len(weak_password["occurrences"]) == 2
    assert weak_password["occurrences"][0]["status"] == "ok"
    assert weak_password["occurrences"][0]["details"] == {
        "password": "StrongP@ssw0rd123",
    }
    assert weak_password["occurrences"][1]["status"] == "ok"
    assert weak_password["occurrences"][1]["details"] == {
        "password": "StrongP@ssw0rd456",
    }

    # Check ldap_anonymous control
    ldap = [e for e in data["controls"] if e["name"] == "ldap_anonymous"][0]
    assert ldap["name"] == "ldap_anonymous"
    assert ldap["max_severity"] == "high"
    assert ldap["confidence"] == "certain"
    assert ldap["status"] == "ko"  # Overall status is KO if any occurrence is KO
    assert ldap["total_status_ok"] == 3
    assert ldap["total_status_ko"] == 2
    assert ldap["total_occurrences"] == 5
    assert set(ldap["all_keys"]) == {"ip", "port"}  # Check all_keys

    # Check ldap_anonymous occurrences
    assert len(ldap["occurrences"]) == 5
    assert ldap["occurrences"][0]["status"] == "ko"
    assert ldap["occurrences"][0]["details"] == {
        "ip": "192.168.1.100",
        "port": 389,
    }
    assert ldap["occurrences"][1]["status"] == "ko"
    assert ldap["occurrences"][1]["details"] == {
        "ip": "192.168.1.101",
        "port": 389,
    }
    assert ldap["occurrences"][2]["status"] == "ok"
    assert ldap["occurrences"][2]["details"] == {
        "ip": "192.168.1.102",
        "port": 389,
    }
    assert ldap["occurrences"][3]["status"] == "ok"
    assert ldap["occurrences"][3]["details"] == {
        "ip": "192.168.1.103",
        "port": 389,
    }
    assert ldap["occurrences"][4]["status"] == "ok"
    assert ldap["occurrences"][4]["details"] == {
        "ip": "192.168.1.104",
        "port": 389,
    }

    # Check observation list has one item (only the ldap_anonymous control with KO occurrences)
    assert len(data["observations"]) == 1
    observation = data["observations"][0]
    assert observation["name"] == "ldap_anonymous"
    assert observation["max_severity"] == "high"
    assert observation["confidence"] == "certain"
    assert observation["total_occurrences"] == 2  # Only KO occurrences
    assert set(observation["all_keys"]) == {"ip", "port"}  # Check all_keys

    # Check observation occurrences (only KO occurrences)
    assert len(observation["occurrences"]) == 2
    assert observation["occurrences"][0]["severity"] == "high"
    assert observation["occurrences"][0]["details"] == {
        "ip": "192.168.1.100",
        "port": 389,
    }
    assert observation["occurrences"][1]["severity"] == "high"
    assert observation["occurrences"][1]["details"] == {
        "ip": "192.168.1.101",
        "port": 389,
    }

    # Check summary
    summary = data["summary"]
    assert summary["total_control_definitions"] == 2
    assert summary["total_control_occurrences"] == 7
    assert (
        summary["total_observations_definitions"] == 1
    )  # Only ldap_anonymous with KO occurrences
    assert (
        summary["total_observations_occurrences"] == 2
    )  # Only 2 KO occurrences from ldap_anonymous

    # Check severity stats
    assert summary["controls_definitions_by_severity"] == {
        "critical": 0,
        "high": 1,
        "medium": 1,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_definitions_by_severity"] == {
        "critical": 0,
        "high": 1,  # Only ldap_anonymous with KO occurrences
        "medium": 0,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }
    assert summary["observations_occurrences_by_severity"] == {
        "critical": 0,
        "high": 2,  # Only 2 KO occurrences from ldap_anonymous
        "medium": 0,
        "low": 0,
        "info": 0,
        "unknown": 0,
    }


def test_json_report_control_max_severity_and_confidence(new_cyberdb):
    # Create weak_password control definition
    c_weak_password = new_cyberdb.feed(
        "control_definition",
        name="weak_password",
        severity="medium",
    )[0]

    # Add first occurrence with medium severity and firm confidence
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="firm",
        control_definition=c_weak_password,
        details={
            "password": "azerty1",
        },
    )
    # Add second occurrence with low severity and certain confidence
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="low",
        confidence="certain",
        control_definition=c_weak_password,
        details={
            "password": "azerty2",
        },
    )

    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check control has max_severity=medium (highest severity) and confidence=firm (highest confidence)
    control = data["controls"][0]
    assert control["max_severity"] == "medium"
    assert control["confidence"] == "firm"


def test_json_report_different_keys(new_cyberdb):
    """Test that all_keys correctly handles different keys across occurrences."""
    c_mixed = new_cyberdb.feed(
        "control_definition",
        name="mixed_keys",
        severity="medium",
    )[0]

    # Add occurrences with different keys
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="certain",
        control_definition=c_mixed,
        details={
            "key1": "value1",
            "key2": "value2",
        },
    )
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="certain",
        control_definition=c_mixed,
        details={
            "key2": "value3",
            "key3": "value4",
        },
    )

    reporter = pm_reporters["controls_json"](new_cyberdb)
    data = reporter.do_processing()

    # Check control
    control = data["controls"][0]
    assert control["name"] == "mixed_keys"
    assert set(control["all_keys"]) == {"key1", "key2", "key3"}  # All unique keys

    # Check observation (should have same keys)
    observation = data["observations"][0]
    assert observation["name"] == "mixed_keys"
    assert set(observation["all_keys"]) == {"key1", "key2", "key3"}  # All unique keys


@pytest.mark.skip
def test_json_report_undefined_severity(new_cyberdb):
    """Test that controls with undefined severity don't raise errors."""
    # Create a control definition with undefined severity
    c_undefined = new_cyberdb.feed(
        "control_definition",
        name="undefined_severity",
    )[0]

    # Add an occurrence with undefined severity
    new_cyberdb.feed(
        "control",
        status="ko",
        control_definition=c_undefined,
        details={
            "test": "value",
        },
    )

    new_cyberdb.feed(
        "control",
        status="ko",
        severity="undefined",  # Explicitly set to None
        control_definition=c_undefined,
        details={
            "test": "value",
        },
    )
    # Just verify it runs without error
    reporter = pm_reporters["controls_json"](new_cyberdb)
    reporter.do_processing()


def test_json_report_latest_run_filtering(new_cyberdb):
    """Test that controls are properly filtered based on latest_run."""
    # Create a control definition
    c_test = new_cyberdb.feed(
        "control_definition",
        name="test_control",
    )[0]

    # Create a run object
    run = new_cyberdb.create("run")

    # Add two controls - one with run and one without
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="certain",
        control_definition=c_test,
        latest_run=run,
        details={},
    )
    new_cyberdb.feed(
        "control",
        status="ko",
        severity="medium",
        confidence="certain",
        control_definition=c_test,
        details={},
    )

    # Test without latest_run filter
    reporter = pm_reporters["controls_json"](new_cyberdb)
    reporter.configure(latest_run=run)
    data = reporter.do_processing()

    # Should only see the control with the specified run
    assert len(data["controls"]) == 1
    control = data["controls"][0]
    assert len(control["occurrences"]) == 1
