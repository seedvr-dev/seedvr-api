        """Minimal SeedVR2 example: create one prediction and print the output URL(s)."""
        import seedvr_api

        output = seedvr_api.run({
    "image_url": "https://example.com/input.png"
})
        print(output)
