FROM lmurawsk/python2.7
RUN apt-get update && apt-get install gcc python-tk libasound2 -y; \
    python -m pip install cx_Freeze==5
RUN python -m pip install pygame numpy requests Pillow

# run docker run --rm -ti --net=host -v `pwd`:/opt -v $HOME/.Xauthority:/root/.Xauthority:ro usm/python2.7 bash
# then run
# export DISPLAY=:0.0
# and last run
# python setup.py build
