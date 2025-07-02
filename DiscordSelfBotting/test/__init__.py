from pytest import fixture

@fixture
def sample_fixture():
    return "sample"

def test_sample(sample_fixture):
    assert sample_fixture == "sample"