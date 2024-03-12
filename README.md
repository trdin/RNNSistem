# RNN service 

## Description

This project utilizes an LSTM (Long Short-Term Memory) model for making predictions. It involves time-series forecasting or sequential data analysis, where LSTM is well-suited due to its ability to retain information over long periods.

## Installation

This project utilizes Poetry for package management. Ensure you have Poetry installed, then run:

```bash
poetry install
```

## Usage

To run tests, execute:

```bash
poetry run pytest
```

Additionally, there are scripts provided:

- `serve`: For serving the model.
- `data`: For managing data.

## Dependencies

This project has the following dependencies:

- Python >=3.9,<3.11
- pandas ^2.2.1
- tensorflow-io-gcs-filesystem 0.27.0
- tensorflow ~2.10
- numpy ^1.26.4
- matplotlib ^3.8.3
- joblib ^1.3.2
- flask ^3.0.2
- requests ^2.31.0
- scikit-learn ^1.4.1.post1
- datetime ^5.4

For development, it additionally requires:

- pytest ^8.1.1

## GitHub Actions

This project is integrated with GitHub Actions. Upon push or pull request to the `main` branch, it automatically installs Python dependencies, runs tests, and lints the code.

## License

This project is licensed under the [MIT License](LICENSE).
