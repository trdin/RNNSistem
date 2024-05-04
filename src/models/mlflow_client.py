import mlflow

def download_model(station_name, stage):
    model_name = f"model={station_name}"

    try:
        client = mlflow.MlflowClient()
        model = mlflow.sklearn.load_model( client.get_latest_versions(name=model_name, stages=[stage])[0].source)

        return model
    except IndexError:
        print(f"Error downloading {stage}, {model_name}")
        return None


def download_scaler(station_name, scaler_type, stage):
    scaler_name = f"{scaler_type}={station_name}"

    try:
        client = mlflow.MlflowClient()
        scaler = mlflow.sklearn.load_model(client.get_latest_versions(name=scaler_name, stages=[stage])[0].source)
        return scaler
    except IndexError:
        print(f"Error downloading {stage}, {scaler_name}")
        return None
    

def mlflow_save_scaler(client, scaler_type, scaler, station_name):
    metadata = {
        "station_name": station_name,
        "scaler_type": scaler_type,
        "expected_features": scaler.n_features_in_,
        "feature_range": scaler.feature_range,
    }

    scaler = mlflow.sklearn.log_model(
        sk_model=scaler,
        artifact_path=f"models/{station_name}/{scaler_type}",
        registered_model_name=f"{scaler_type}={station_name}",
        metadata=metadata,
    )

    scaler_version = client.create_model_version(
        name=f"{scaler_type}={station_name}",
        source=scaler.model_uri,
        run_id=scaler.run_id
    )

    client.transition_model_version_stage(
        name=f"{scaler_type}={station_name}",
        version=scaler_version.version,
        stage="staging",
    )

def mlflow_save_model(model, station_name, client):
    metadata = {
        "station_name": station_name,
        "model_type": "LSTM",
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
    }

    station_model = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=f"models/{station_name}/model",
            registered_model_name=f"model={station_name}",
            metadata=metadata
        )
    
    model_version = client.create_model_version(
            name=f"model={station_name}",
            source=station_model.model_uri,
            run_id=station_model.run_id
        )

    client.transition_model_version_stage(
        name=f"model={station_name}",
        version=model_version.version,
        stage="staging",
    )



def prod_model_save(station_name):

    try:
        client = mlflow.MlflowClient()

        model_version = client.get_latest_versions(name= f"model={station_name}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"model={station_name}", model_version, "production")

        stands_scaler_version = client.get_latest_versions(name=f"stands_scaler={station_name}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"stands_scaler={station_name}", stands_scaler_version, "production")
        
        other_scaler_version = client.get_latest_versions(name= f"other_scaler={station_name}", stages=["staging"])[0].version
        client.transition_model_version_stage(f"other_scaler={station_name}", other_scaler_version, "production")


    except IndexError:
        print(f"#####error##### \n replace_prod_model {station_name}")
        return