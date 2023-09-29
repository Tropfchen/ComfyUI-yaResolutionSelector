import re


class Dimensions:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value):
        if value < 64:
            raise ValueError("width of less than 64 pixel")
        self._width = int(value / 2) * 2 if value % 2 else int(value)

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value):
        if value < 64:
            raise ValueError("height of less than 64 pixel")
        self._height = int(value / 2) * 2 if value % 2 else int(value)


def calculate_aspect_ratio(
    base_resolution: int, ratio: float, overextend: bool
) -> Dimensions:
    width = base_resolution
    height = base_resolution

    if overextend:
        if ratio > 1:
            height *= ratio
        else:
            width /= ratio
    else:
        if ratio > 1:
            width /= ratio
        else:
            height *= ratio

    return Dimensions(width, height)


def calculate_constant_constant_resolution(
    base_resolution: int, ratio: float
) -> Dimensions:
    pixel_count = base_resolution**2
    new_height = (pixel_count * ratio) ** 0.5
    new_width = new_height / ratio
    return Dimensions(new_width, new_height)


class YARS:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        ratios = [
            "1:1",
            "landscape (4:3)",
            "landscape (3:2)",
            "landscape (16:9)",
            "landscape (16:10)",
            "landscape (21:9)",
            "portrait (3:4)",
            "portrait (2:3)",
            "portrait (9:16)",
            "portrait (9:10)",
            "portrait (9:21)",
        ]

        return {
            "required": {
                "base_resolution": (
                    "INT",
                    {
                        "default": 512,
                        "min": 512,
                        "max": 8192,
                        "step": 128,
                    },
                ),
                "aspect_ratio": ((ratios),),
                "overextend": (
                    "BOOLEAN",
                    {"default": False, "label_on": "yes ", "label_off": "no "},
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "calculate"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def calculate(
        self,
        base_resolution: int,
        aspect_ratio: str,
        overextend: bool,
    ) -> tuple[int, int]:
        if m := re.search(r"(\d+):(\d+)", aspect_ratio):
            ratio: float = int(m.group(2)) / int(m.group(1))
            d = calculate_aspect_ratio(base_resolution, ratio, overextend)

            return (d.width, d.height)

        raise ValueError(f"Could't find aspect ratio in string `{aspect_ratio}`")


class YARSAdv:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "base_resolution": (
                    "INT",
                    {
                        "default": 512,
                        "min": 512,
                        "max": 8192,
                        "step": 128,
                    },
                ),
                "width_ratio": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 1024,
                        "step": 1,
                    },
                ),
                "height_ratio": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 1024,
                        "step": 1,
                    },
                ),
                "overextend": (
                    "BOOLEAN",
                    {"default": False, "label_on": "yes ", "label_off": "no "},
                ),
                "constant_resolution": (
                    "BOOLEAN",
                    {"default": False, "label_on": "yes ", "label_off": "no "},
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "calculate"
    OUTPUT_NODE = False
    CATEGORY = "utils"

    def calculate(
        self,
        base_resolution: int,
        width_ratio: int,
        height_ratio: int,
        overextend: bool,
        constant_resolution: bool,
    ) -> tuple[int, int]:
        ratio: float = height_ratio / width_ratio

        if constant_resolution:
            d = calculate_constant_constant_resolution(base_resolution, ratio)
        else:
            d = calculate_aspect_ratio(base_resolution, ratio, overextend)

        return (d.width, d.height)


if __name__ == "__main__":
    import unittest

    class TestDimensions(unittest.TestCase):
        def test_constant_resolution_calculates_correct_dimensions(self):
            d = calculate_constant_constant_resolution(1024, 1)
            self.assertEqual((d.width, d.height), (1024, 1024), "Incorrect dimensions")

        def test_constant_resolution_calculates_correct_aspect_ratio(self):
            d = calculate_constant_constant_resolution(1024, 4 / 3)
            self.assertAlmostEqual(
                d.height / d.width, 4 / 3, 2, "Incorrect aspect ratio"
            )

        def test_constant_resolution_calculates_correct_pixel_count(self):
            d = calculate_constant_constant_resolution(1024, 4 / 3)
            self.assertEqual(d.width * d.height, 1047252, "Incorrect pixel count")

        def test_calculate_dimensions_with_false_overextend(self):
            d = calculate_aspect_ratio(1024, 4 / 3, False)
            self.assertEqual(
                (d.width, d.height),
                (768, 1024),
                "Incorrect dimensions without overextending",
            )

        def test_calculate_dimensions_with_true_overextend(self):
            d = calculate_aspect_ratio(512, 4 / 3, True)
            self.assertEqual(
                (d.width, d.height),
                (512, 682),
                "Incorrect dimensions with overextending",
            )

        def test_cleanup_dimensions_raises_error_with_low_height(self):
            with self.assertRaises(
                ValueError, msg="No error raised with height less than 64 pixels"
            ):
                Dimensions(512, 60)

        def test_cleanup_dimensions_raises_error_with_low_width(self):
            with self.assertRaises(
                ValueError, msg="No error raised with width less than 64 pixels"
            ):
                Dimensions(55, 512)

        def test_dimensions_returns_ints(self):
            d = Dimensions(153.584, 128.0000)
            self.assertIsInstance(d.width, int)
            self.assertIsInstance(d.height, int)

    unittest.main()
