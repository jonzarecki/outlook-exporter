import os
import subprocess


def main():
    subprocess.call(rf"streamlit run {os.path.join(os.path.dirname(__file__), 'run_streamlit.py')}")


if __name__ == "__main__":
    main()
