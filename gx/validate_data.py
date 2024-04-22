# %%
import great_expectations as gx
import sys

context = gx.get_context()

# %%
result = context.run_checkpoint(checkpoint_name="station_1_checkpoint")

# %%
if not result["success"]:
    print("Validation failed!")
    sys.exit(1)

print("Validation succeeded!")


