class SimpleSizePicker:
    @classmethod
    def INPUT_TYPES(s):
        square_resolutions = [
            "512 x 512 (1:1)",
            "768 x 768 (1:1)",
            "1024 x 1024 (1:1)",
            "1536 x 1536 (1:1)",
            "2048 x 2048 (1:1)"
        ]
        portrait_resolutions = [
            "512 x 768 (2:3)",
            "768 x 1152 (2:3)",
            "1024 x 1536 (2:3)",
            "1152 x 1728 (2:3)",
            "832 x 1216 (≈3:4)",
            "1024 x 1360 (≈3:4)",
            "1080 x 1920 (9:16)"
        ]
        landscape_resolutions = [
            "768 x 512 (3:2)",
            "1152 x 768 (3:2)",
            "1536 x 1024 (3:2)",
            "1216 x 832 (≈4:3)",
            "1360 x 1024 (≈4:3)",
            "1920 x 1080 (16:9)",
            "2048 x 1152 (16:9)",
            "2560 x 1440 (16:9)",
            "3840 x 2160 (16:9)"
        ]
        widescreen_resolutions = [
            "1344 x 768 (16:9)",
            "1792 x 1024 (16:9)",
            "2048 x 1080 (≈17:9, DCI 2K)"
        ]
        ultrawide_resolutions = [
            "2560 x 1080 (64:27 ≈ 21:9)",
            "3440 x 1440 (43:18 ≈ 21.5:9)",
            "3840 x 1600 (12:5 = 21.6:9)",
            "5120 x 2160 (64:27 ≈ 21:9, 5K UW)"
        ]
        super_ultrawide_resolutions = [
            "3840 x 1080 (32:9, Dual Full HD)",
            "5120 x 1440 (32:9, Dual QHD)",
            "7680 x 2160 (32:9, 8K Ultra Wide)"
        ]
        panoramic_resolutions = [
            "5760 x 1080 (48:9 = 16:3, Triple Full HD)",
            "7680 x 1440 (48:9 = 16:3, Triple QHD)",
            "9600 x 1200 (8:1, Custom Ultra Panoramic)"
        ]
        resolutions = (
                square_resolutions +
                portrait_resolutions +
                landscape_resolutions +
                widescreen_resolutions +
                ultrawide_resolutions +
                super_ultrawide_resolutions +
                panoramic_resolutions
        )

        return {
            "required": {
                "resolution": (resolutions, {"default": square_resolutions[0]}),
            }
        }

    RETURN_TYPES = ("INT","INT",)
    RETURN_NAMES = ("width","height",)
    FUNCTION = "execute"
    CATEGORY = "BishaNodes"

    def execute(self, resolution):
        width, height = map(int, resolution.split(" (")[0].split(" x "))

        return (width, height,)

MISC_CLASS_MAPPINGS = {
    "SimpleSizePicker": SimpleSizePicker,
}

MISC_NAME_MAPPINGS = {
    "SimpleSizePicker": "Simple Size Picker",
}