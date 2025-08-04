#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Optimized version of test_challenges.py demonstrating performance improvements.

This file shows the before/after comparison using the new fixture-based approach
instead of create_ctfd/destroy_ctfd pattern.
"""

from freezegun import freeze_time

from CTFd.models import Challenges, Flags, Hints, Solves, Tags, Users
from CTFd.utils import set_config


def test_api_challenges_get_visibility_public_optimized(app, client):
    """
    OPTIMIZED: Can a public user get /api/v1/challenges if challenge_visibility is private/public
    
    This test uses the new fixture pattern instead of create_ctfd/destroy_ctfd.
    """
    set_config("challenge_visibility", "public")
    r = client.get("/api/v1/challenges")
    assert r.status_code == 200
    
    set_config("challenge_visibility", "private")
    r = client.get("/api/v1/challenges", json="")
    assert r.status_code == 403


def test_api_challenges_get_ctftime_public_optimized(app, client):
    """
    OPTIMIZED: Can a public user get /api/v1/challenges if ctftime is over
    """
    with freeze_time("2017-10-7"):
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        
        set_config("start", "1507089600")  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config("end", "1507262400")    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        
        r = client.get("/api/v1/challenges")
        assert r.status_code == 403


def test_api_challenges_get_logged_in_optimized(app, admin_client, challenge_factory, flag_factory):
    """
    OPTIMIZED: Can a logged in user get /api/v1/challenges
    
    Uses factory fixtures instead of direct helper calls.
    """
    chal = challenge_factory()
    flag_factory(challenge_id=chal.id, content="flag")
    
    r = admin_client.get("/api/v1/challenges")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert len(data) == 1


def test_api_challenges_post_non_admin_optimized(app, client, user_factory):
    """
    OPTIMIZED: Can a non-admin user post /api/v1/challenges
    """
    user = user_factory()
    
    with client.session_transaction() as sess:
        sess["id"] = user.id
        sess["nonce"] = "fake-nonce"
        sess["hash"] = "fake-hash"
    
    challenge_data = {
        "name": "name",
        "category": "category", 
        "description": "description",
        "value": 100,
        "state": "hidden",
        "type": "standard",
    }
    
    r = client.post("/api/v1/challenges", json=challenge_data)
    assert r.status_code == 403


def test_api_challenges_post_admin_optimized(app, admin_client):
    """
    OPTIMIZED: Can an admin user post /api/v1/challenges
    """
    challenge_data = {
        "name": "name",
        "category": "category",
        "description": "description", 
        "value": 100,
        "state": "hidden",
        "type": "standard",
    }
    
    r = admin_client.post("/api/v1/challenges", json=challenge_data)
    assert r.status_code == 200
    assert r.get_json().get("data")["id"] == 1
    
    r = admin_client.get("/api/v1/challenges/1")
    assert r.status_code == 200
    assert r.get_json().get("data")["id"] == 1


def test_api_challenges_get_solves_optimized(app, admin_client, challenge_factory, flag_factory, user_factory):
    """
    OPTIMIZED: Can a user get /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public
    """
    chal = challenge_factory()
    flag = flag_factory(challenge_id=chal.id, content="flag")
    user = user_factory()
    
    from tests.helpers import gen_solve
    gen_solve(app.db, user_id=user.id, challenge_id=chal.id, provided=flag.content)
    
    r = admin_client.get(f"/api/v1/challenges/{chal.id}/solves")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert len(data) == 1
    assert data[0]["account_id"] == user.id


def test_api_challenges_get_fails_optimized(app, admin_client, challenge_factory, user_factory):
    """
    OPTIMIZED: Can a user get /api/v1/challenges/<challenge_id>/fails if challenge_visibility is private/public
    """
    chal = challenge_factory()
    user = user_factory()
    
    from tests.helpers import gen_fail
    gen_fail(app.db, user_id=user.id, challenge_id=chal.id, provided="wrong_flag")
    
    r = admin_client.get(f"/api/v1/challenges/{chal.id}/fails")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert len(data) == 1
    assert data[0]["account_id"] == user.id


# Example of more complex test optimization
def test_api_challenges_attempt_submission_optimized(app, client, challenge_factory, flag_factory, user_factory):
    """
    OPTIMIZED: Test challenge submission with proper fixture usage
    """
    user = user_factory()
    chal = challenge_factory()
    flag = flag_factory(challenge_id=chal.id, content="correct_flag")
    
    # Login user
    with client.session_transaction() as sess:
        sess["id"] = user.id
        sess["nonce"] = "fake-nonce"
        sess["hash"] = "fake-hash"
    
    # Submit correct flag
    r = client.post(f"/api/v1/challenges/{chal.id}/attempts", json={"submission": "correct_flag"})
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["status"] == "correct"
    
    # Verify solve was recorded
    assert Solves.query.filter_by(user_id=user.id, challenge_id=chal.id).count() == 1