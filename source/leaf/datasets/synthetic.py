"""Synthetic problem dataset generator and provider for offline testing."""

from leaf.schemas.enums import Language, TemporalCohort
from leaf.schemas.problem import Problem, ReferenceSolution, TestCase


def get_synthetic_problems() -> list[Problem]:
    """Generate a suite of 5 synthetic problems designed to validate all benchmark execution paths.

    Covers:
    1. Solvable arithmetic problem (Sum of Two Numbers).
    2. String manipulation problem (Reverse String).
    3. Algorithmic timeout / infinite loop challenge.
    4. Memory exhaustion / allocation bomb challenge.
    5. Deliberate syntax / compilation error challenge.
    """
    problems: list[Problem] = []

    # Problem 1: Solvable Arithmetic (Two Sum)
    p1 = Problem(
        problem_id="synth_001_two_sum",
        source="synthetic",
        source_id="001",
        title="Sum of Two Numbers",
        statement="Read two space-separated integers A and B from standard input and print their sum.",
        input_spec="A single line containing two integers A and B (-10^9 <= A, B <= 10^9).",
        output_spec="Print a single integer: A + B.",
        constraints="-10^9 <= A, B <= 10^9",
        tags=["math", "basics"],
        difficulty="easy",
        published_at="2024-01-01T00:00:00Z",
        temporal_cohort=TemporalCohort.HISTORICAL,
        tests=[
            TestCase(input_data="2 3\n", expected_output="5\n", is_hidden=False, test_id="p1_t1"),
            TestCase(input_data="-10 20\n", expected_output="10\n", is_hidden=False, test_id="p1_t2"),
            TestCase(input_data="1000000000 1000000000\n", expected_output="2000000000\n", is_hidden=True, test_id="p1_t3"),
        ],
        reference_solutions=[
            ReferenceSolution(
                code="import sys\na, b = map(int, sys.stdin.read().split())\nprint(a + b)\n",
                language=Language.PYTHON,
                selection_criterion="official_reference",
            ),
            ReferenceSolution(
                code="#include <iostream>\nusing namespace std;\nint main() {\n    long long a, b;\n    if (cin >> a >> b) cout << a + b << endl;\n    return 0;\n}\n",
                language=Language.CPP,
                selection_criterion="official_reference",
            ),
            ReferenceSolution(
                code="import java.util.Scanner;\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextLong()) {\n            long a = sc.nextLong();\n            long b = sc.nextLong();\n            System.out.println(a + b);\n        }\n    }\n}\n",
                language=Language.JAVA,
                selection_criterion="official_reference",
            ),
        ],
    )
    problems.append(p1)

    # Problem 2: String Reverse
    p2 = Problem(
        problem_id="synth_002_reverse_string",
        source="synthetic",
        source_id="002",
        title="Reverse String",
        statement="Read a single non-empty word from standard input and output it reversed.",
        input_spec="A single word consisting of printable ASCII characters.",
        output_spec="The reversed word.",
        constraints="1 <= length <= 1000",
        tags=["strings"],
        difficulty="easy",
        published_at="2024-01-01T00:00:00Z",
        temporal_cohort=TemporalCohort.HISTORICAL,
        tests=[
            TestCase(input_data="hello\n", expected_output="olleh\n", is_hidden=False, test_id="p2_t1"),
            TestCase(input_data="racecar\n", expected_output="racecar\n", is_hidden=True, test_id="p2_t2"),
        ],
        reference_solutions=[
            ReferenceSolution(
                code="import sys\ns = sys.stdin.read().strip()\nprint(s[::-1])\n",
                language=Language.PYTHON,
                selection_criterion="official_reference",
            ),
        ],
    )
    problems.append(p2)

    # Problem 3: Infinite Loop / TLE Test
    p3 = Problem(
        problem_id="synth_003_infinite_loop",
        source="synthetic",
        source_id="003",
        title="Infinite Loop Benchmark",
        statement="Accepts an integer N. If N is 1, halts immediately. If N is 0, enters an infinite loop.",
        input_spec="An integer 0 or 1.",
        output_spec="Outputs 'DONE' if N is 1.",
        difficulty="hard",
        published_at="2026-01-01T00:00:00Z",
        temporal_cohort=TemporalCohort.RECENT,
        tests=[
            TestCase(input_data="1\n", expected_output="DONE\n", is_hidden=False, test_id="p3_t1"),
            TestCase(input_data="0\n", expected_output="DONE\n", is_hidden=True, test_id="p3_t2_tle"),
        ],
        reference_solutions=[
            ReferenceSolution(
                code="import sys, time\nn = int(sys.stdin.read().strip())\nif n == 0:\n    while True:\n        time.sleep(1)\nprint('DONE')\n",
                language=Language.PYTHON,
                selection_criterion="test_suite_trap",
            ),
        ],
    )
    problems.append(p3)

    # Problem 4: Memory Limit Exceeded / OOM Test
    p4 = Problem(
        problem_id="synth_004_memory_bomb",
        source="synthetic",
        source_id="004",
        title="Memory Bomb Benchmark",
        statement="Accepts an integer N (megabytes). If N <= 10, prints OK. If N > 1000, allocates large arrays.",
        input_spec="An integer N representing requested buffer size.",
        output_spec="Outputs 'OK'.",
        difficulty="hard",
        published_at="2026-01-01T00:00:00Z",
        temporal_cohort=TemporalCohort.RECENT,
        tests=[
            TestCase(input_data="5\n", expected_output="OK\n", is_hidden=False, test_id="p4_t1"),
            TestCase(input_data="2000\n", expected_output="OK\n", is_hidden=True, test_id="p4_t2_oom"),
        ],
        reference_solutions=[
            ReferenceSolution(
                code="import sys\nn = int(sys.stdin.read().strip())\nif n > 500:\n    buf = [0] * (500 * 1024 * 1024) # Allocate huge buffer\nprint('OK')\n",
                language=Language.PYTHON,
                selection_criterion="test_suite_trap",
            ),
        ],
    )
    problems.append(p4)

    return problems

