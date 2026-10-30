from verification.confidence_score import calculate_confidence

def test_non_primary_never_verified():
    rec={"official_source_url":"https://example.com/x","evidence":[
        {"field":"name","source_url":"https://example.com/x","snippet":"Test"}]}
    score,status,_=calculate_confidence(rec)
    assert score < 95
    assert status == "REVIEW_REQUIRED"

def test_official_host_with_only_name_not_verified():
    rec={"official_source_url":"https://scholarships.gov.in/x","evidence":[
        {"field":"name","source_url":"https://scholarships.gov.in/x","snippet":"Test"}]}
    score,status,_=calculate_confidence(rec)
    assert score < 95
    assert status == "REVIEW_REQUIRED"
