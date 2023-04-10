# CapStone
pineline // '''v4l2src ! videoconvert ! video/x-raw,format=RGBA !appsink wait-on-eos=false max-buffers=1 drop=true sync=false name=sink'''
          '''v4l2src  ! videoconvert ! video/x-raw,format=RGBA !appsink drop=true sync=false name=sink'''
