TEXT_1 = "1"
TEXT_2 = "2"
TEXT_3 = "3"


SCENARIO = [
    # time, text in_status, out_status, is_end,
    (360, TEXT_1, None, "WAIT", False),
    (2340, TEXT_2, "1", "2", False),
    (93600, TEXT_3, "2", "finish", True),
]
