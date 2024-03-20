from invoke import task


@task
def lambda_set_env(c):
    from src.kakeibo.utils import read_client_secret, read_env

    d = {}
    envs = read_env()
    for k, v in envs.items():
        d[k] = v
    client_secrets = read_client_secret()
    for k, v in client_secrets.items():
        d[f"google_api_{k}"] = v
    c.run(f"aws lambda update-function-configuration --function-name kakeibo --environment Variables={d}", echo=True)
