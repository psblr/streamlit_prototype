# streamlit_prototype

hosted with streamlit at (https://cadgenerator3000.streamlit.app/)

To wake up the app, wait a few seconds. Even if there is an error message, it should start after a while. It can take up two several minutes for GitHub to start the application again0.

else....

# ☕ Development

## Packages
```sh
# create virtual env to not have any version conflicts
python3 -m venv .venv
# activate venv
source .venv/bin/activate
# install packages
pip install -r requirements.txt
```

## Run the app locally

To work on windows, ```start_xvfb()``` needs to be removed (or commented out). It is necessary for streamlit hosting.

```sh
streamlit run streamlit_prototype_idea.py
```
