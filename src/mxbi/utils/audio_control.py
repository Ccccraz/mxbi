import subprocess
from random import choice


# TODO: Determine the probability
def set_volume(monkey: str, frequency: int) -> None:
    db_vector = []
    bt = choice(([[10, 30], [50, 70]])) if monkey == "wolfgang" else []
    at = [80, 80, 80] if monkey == "wolfgang" else [80, 80, 80]
    db_vector = at * 10 + bt

    current_stimulus_intensity = choice(db_vector)
    current_stimulus_frequency = frequency

    master_amp, digital_amp = get_amp_value(
        current_stimulus_frequency, current_stimulus_intensity
    )

    set_master_volume(master_amp)
    set_digital_volume(digital_amp)


def set_master_volume(volume: int) -> None:
    subprocess.run(["amixer", "sset", "Master", f"{volume}%"])


def set_digital_volume(volume: int) -> None:
    subprocess.run(["amixer", "-c", "0", "sset", "Digital", f"{volume}"])


def get_amp_value(freqency: int, amplitude: float) -> tuple[int, int]:
    return masterVals[freqency], digitalVals[amplitude]


masterVals: dict[int, int] = {
    200: 28,
    1000: 28,
    1760: 18,
    2000: 25,
    2640: 22,
    3950: 20,
    4000: 20,
    4700: 20,
    5000: 20,
    5920: 19,
    6000: 19,
    7000: 20,
    10000: 26,
    15000: 24,
    20000: 21,
}

digitalVals: dict[float, int] = {
    0: 0,
    1: 9,
    2: 19,
    3: 29,
    4: 39,
    5: 49,
    10: 59,
    11: 61,
    12: 63,
    13: 65,
    14: 67,
    15: 69,
    16: 71,
    17: 73,
    18: 75,
    19: 77,
    20: 79,
    21: 81,
    22: 83,
    23: 85,
    24: 87,
    25: 89,
    26: 91,
    27: 93,
    28: 95,
    29: 97,
    30: 99,
    31: 101,
    32: 103,
    33: 105,
    34: 107,
    35: 109,
    36: 111,
    37: 113,
    38: 115,
    39: 117,
    40: 119,
    42: 123,
    44: 127,
    45: 129,
    46: 131,
    48: 135,
    50: 139,
    52: 143,
    54: 147,
    55: 149,
    56: 151,
    58: 155,
    60: 159,
    61: 161,
    62: 163,
    63: 165,
    64: 167,
    65: 169,
    66: 171,
    67: 173,
    67.5: 174,
    68: 175,
    68.5: 176,
    69: 177,
    69.5: 178,
    70: 179,
    70.5: 180,
    71: 181,
    71.5: 182,
    72: 183,
    72.5: 184,
    73: 185,
    74: 187,
    75: 189,
    76: 191,
    77: 193,
    78: 195,
    79: 197,
    80: 199,
    82: 203,
    84: 207,
}
