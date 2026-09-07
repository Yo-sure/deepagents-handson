def pytest_addoption(parser):
    parser.addoption("--build-student", action="store_true", help="직접 완성하기의 학생 구현을 검사합니다.")
