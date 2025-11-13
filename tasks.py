from invoke import task


@task
def lambda_set_env(c, profile, function_name):
    from libs.kakeibo.kakeibo.utils import read_client_secret, read_env

    d = {}
    envs = read_env()
    for k, v in envs.items():
        d[k] = v
    client_secrets = read_client_secret()
    for k, v in client_secrets.items():
        d[f"google_api_{k}"] = v
    variables = ",".join([f"{k}={v}" for k, v in d.items()])
    variables = "{" + variables + "}"
    cmd = f'aws lambda update-function-configuration --profile {profile} --function-name {function_name} --environment "Variables={variables}"'
    c.run(cmd, echo=True)
