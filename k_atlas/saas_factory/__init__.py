try:
    from k_atlas.saas_factory.saas_command_pipeline import run_saas_factory
except ModuleNotFoundError:
    def run_saas_factory(*args, **kwargs):
        raise ModuleNotFoundError(
            "k_atlas.saas_factory.saas_command_pipeline is not available in this workspace"
        )
