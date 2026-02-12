"""Tests for state management across handlers."""
from handlers import login, assessment, lms


class TestLoginState:
    def test_detail_collection_mode(self):
        cid = 99999
        assert login.is_in_detail_collection_mode(cid) is False

        login.user_detail_collection[cid] = {"step": "name"}
        assert login.is_in_detail_collection_mode(cid) is True

        del login.user_detail_collection[cid]
        assert login.is_in_detail_collection_mode(cid) is False

    def test_login_other_mode(self):
        cid = 99998
        assert login.is_in_login_other_mode(cid) is False

        login.user_login_other_mode[cid] = "skillserv"
        assert login.is_in_login_other_mode(cid) is True

        login.user_login_other_mode[cid] = None
        assert login.is_in_login_other_mode(cid) is False


class TestAssessmentState:
    def test_detail_collection_mode(self):
        cid = 99997
        assert assessment.is_in_assessment_detail_collection_mode(cid) is False

        assessment.user_assessment_detail_collection[cid] = {"step": "name"}
        assert assessment.is_in_assessment_detail_collection_mode(cid) is True

        del assessment.user_assessment_detail_collection[cid]
        assert assessment.is_in_assessment_detail_collection_mode(cid) is False

    def test_other_mode(self):
        cid = 99996
        assert assessment.is_in_assessment_other_mode(cid) is False

        assessment.user_assessment_other_mode[cid] = {"active": True, "type": "pcq"}
        assert assessment.is_in_assessment_other_mode(cid) is True

        assessment.user_assessment_other_mode[cid] = {"active": False, "type": ""}
        assert assessment.is_in_assessment_other_mode(cid) is False


class TestLmsState:
    def test_detail_collection_mode(self):
        cid = 99995
        assert lms.is_in_lms_detail_collection_mode(cid) is False

        lms.user_lms_detail_collection[cid] = {"step": "name"}
        assert lms.is_in_lms_detail_collection_mode(cid) is True

        del lms.user_lms_detail_collection[cid]
        assert lms.is_in_lms_detail_collection_mode(cid) is False

    def test_other_mode(self):
        cid = 99994
        assert lms.is_in_lms_other_mode(cid) is False

        lms.user_lms_other_mode[cid] = True
        assert lms.is_in_lms_other_mode(cid) is True

        lms.user_lms_other_mode[cid] = False
        assert lms.is_in_lms_other_mode(cid) is False
