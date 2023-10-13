from ricxappframe.xapp_sdl import XappSdl

def sdl_health_check():
    try:
        # Initialize SDL interface
        sdl = XappSdl()

        # Perform a simple write operation
        sdl.set("health_check", "test_key", "test_value")

        # Perform a read operation
        value = sdl.get("health_check", "test_key")

        # Verify the operation
        if value == "test_value":
            print("SDL Health Check: PASS")
        else:
            print("SDL Health Check: FAIL")

    except Exception as e:
        print(f"SDL Health Check: EXCEPTION - {str(e)}")

# If running this file directly, execute the SDL health check
if __name__ == "__main__":
    sdl_health_check()

