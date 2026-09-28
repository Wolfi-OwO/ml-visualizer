<div align="center">

# ML Visualizer

**Four classical machine learning algorithms, explained by watching them run.**
A Streamlit app where every plot is live: drag a slider and the gradient descent step, the perceptron weight or the KNN classification recomputes in front of you.

[![pipeline status](https://gitlab.com/WoofiOwO/5bhif-datascience-webapp/badges/main/pipeline.svg)](https://gitlab.com/WoofiOwO/5bhif-datascience-webapp/-/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-ff4b4b?logo=streamlit&logoColor=white)

</div>

![ML Visualizer — starting the gradient descent animation and watching the step marker roll down the curve](docs/demo/ml-visualizer-demo.gif)

<div align="center"><sub>Starting the Gradient Descent animation and watching it step down the curve.<br/>Also available as <a href="docs/demo/ml-visualizer-demo.mp4">full-resolution video</a> (60 fps).</sub></div>

## Features

### Home

![ML Visualizer homepage — links to the four algorithm pages with a short explanation of each](docs/screenshots/homepage.png)

- Landing page (in German, like the rest of the app) that explains in three short paragraphs what each of the four pages does and where it gets interesting to poke at — an unreasonable learning rate, a `k` larger than half the point cloud.

### Gradient Descent

![Gradient Descent Visualizer — a parabola with the current step marked, sliders for start value, learning rate and iteration count](docs/screenshots/gradient-descent.png)

- Minimizes `f(x) = 0.5x²` from a configurable start value, learning rate and iteration count, either step-by-step or animated with Start/Stop.
- The step history is memoized with `st.cache_data`, so replaying the same parameters (e.g. after switching tabs and back) does not recompute it.

### Perceptron

![Perceptron page — a single neuron diagram with live weight, bias and output values, trained on the AND truth table](docs/screenshots/perceptron.png)

- A single neuron with two inputs, trained on the AND truth table, with the diagram, current weights, bias and epoch stepping through training live.
- Learning rate, epoch count and the random seed used to initialize the weights are all adjustable, so a run is reproducible.

### KNN Visualizer

![K-Nearest Neighbors page — a scatter plot of two labeled point clusters and unclassified points to be labeled](docs/screenshots/knn-visualizer.png)

- Add points by hand or start from a seeded two-cluster point cloud, pick `k`, and classify — unlabeled points take the majority class of their `k` nearest neighbors.

### Neural Network

![Neuronales Netz page — a 2-2-1 network diagram with per-neuron weights, activations, loss and accuracy for the AND function](docs/screenshots/neural-network.png)

- The same AND function as the perceptron page, this time with a hidden layer and backpropagation, showing every weight, the hidden-layer activations and the loss/accuracy curve per epoch.
- Snapshots per training epoch let you scrub back through a run instead of only ever seeing the final weights.

## Why it is built this way

- Every algorithm lives on its own `st.Page` (`src/pages/*.py`) registered in `src/app.py` — no shared page router to keep in sync, and a page can be added or removed without touching the others.
- Random seeds (perceptron init, the KNN starting cloud, the neural net's weight init) are fixed by default rather than reseeded per run, so a demo is reproducible instead of a different plot on every reload.
- The app deploys to **Azure Container Apps**, which scale to zero when idle. `infrastructure/deploy-scripts/4.setup-appservice.sh` targets an older, PaaS-based Azure hosting model and is a leftover from an earlier iteration; the scripts GitLab CI actually runs (`5.configure-container-app-acr.sh` and the inline `az containerapp` calls in `.gitlab-ci.yml`) are the current path.

## Tech stack

| Layer         | Tech                                                     |
| ------------- | --------------------------------------------------------- |
| Application   | Python 3.12, Streamlit, NumPy, Pandas, Altair, Plotly     |
| Testing       | pytest, pytest-cov                                        |
| Code quality  | Ruff, Black, pre-commit                                   |
| Container     | Docker (multi-stage build), Docker Compose                |
| CI/CD         | GitLab CI                                                  |
| Cloud         | Azure Container Apps, Azure Container Registry            |

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py
```

Visit <http://localhost:8501>.

Or with Docker:

```bash
docker compose -f docker/docker-compose.dev.yml up
```

Run the tests:

```bash
pip install -r requirements.txt
pytest src/tests/ -v --cov=src
```

## Project structure

```text
.
├── src/                          # Application source
│   ├── app.py                    # Entry point — registers the pages, renders the footer
│   ├── pages/                    # One file per algorithm (homepage, gradient-descent, perceptron, knn-visualize, neuronal-net)
│   ├── utils/                    # Config, versioning, theme colors, neural-network math
│   ├── styles/                   # Sidebar and page CSS
│   └── tests/                    # pytest suite (pages, algorithms, utils, integration)
├── docker/                       # Per-environment Compose files and the dev Dockerfile
├── infrastructure/deploy-scripts/ # Azure CLI scripts (resource group, ACR, Container App)
├── landing/                       # Static marketing page served separately from the Streamlit app
├── organizational/                # Project-management notes (test plans, GitLab API scratch requests)
├── Dockerfile                     # Production image
├── .gitlab-ci.yml                 # Pipeline: validate → lint → test → security → build → deploy → release
└── requirements.txt
```

## CI/CD

`.gitlab-ci.yml` runs `validate → lint → test → security → build → deploy:review → deploy:production → release → pages → cleanup`. Merge requests get an ephemeral Container App review environment (auto-stopped after a day); pushes to `main` build the image, push it to ACR, and roll it out to the production Container App with a health check before the old revision is retired. GitLab's SAST and dependency-scanning templates run in the security stage.

## License

MIT, see [LICENSE](./LICENSE).
