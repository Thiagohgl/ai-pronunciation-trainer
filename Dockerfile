FROM registry.gitlab.com/aletrn/ai-pronunciation-trainer:0.5.0

ARG ARCH
ARG WORKDIR_ROOT
ENV PYTHONPATH="${WORKDIR_ROOT}:${WORKDIR_ROOT}/.venv:${PYTHONPATH}:/usr/local/lib/python3/dist-packages"
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV IS_DOCKER_CONTAINER="YES"
ENV LOG_JSON_FORMAT="TRUE"
ENV LOG_LEVEL="INFO"

ENV VIRTUAL_ENV=${WORKDIR_ROOT}/.venv PATH="${WORKDIR_ROOT}/.venv/bin:$PATH"

COPY --chown=python:python . ${WORKDIR_ROOT}/.

RUN python --version
RUN pip list
RUN echo "PATH: ${PATH}."
RUN echo "WORKDIR_ROOT: ${WORKDIR_ROOT}."
RUN ls -l ${WORKDIR_ROOT}
RUN ls -ld ${WORKDIR_ROOT}
RUN python -c "import sys; print(sys.path)"
RUN python -c "import epitran"
RUN python -c "import flask"
RUN python -c "import pandas"
RUN python -c "from torch import Tensor"
RUN python -c "import gunicorn"
RUN df -h
RUN ls -l ${WORKDIR_ROOT}/webApp.py
RUN ls -l ${WORKDIR_ROOT}/static/

USER 999
ENV PATH="${WORKDIR_ROOT}:${WORKDIR_ROOT}/.venv/bin:$PATH"
RUN echo "PATH: $PATH ..."
RUN echo "PYTHONPATH: $PYTHONPATH ..."
RUN echo "MPLCONFIGDIR: $MPLCONFIGDIR ..."

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "webApp:app"]
