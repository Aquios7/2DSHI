import cv2
# Windows OS
# from stream_tools.curveDigitizer import run as runCurve
# from experiment_set_up import user_input_validation as uiv
# from constants import STEP_DESCRIPTIONS as sd
# Linux OS
from stream_tools.curveDigitizer import run as runCurve
from experiment_set_up import user_input_validation as uiv
from constants import STEP_DESCRIPTIONS as sd
from gui import popups

def step_one(stream, histogram, continue_stream):
    if stream.args.verbose:
        print("""
        Step 1
        This step streams the raw camera feed.
    
        Args:
            stream (Stream): An instance of the Stream Class
            histogram (bool): True if you'd like to display histograms for pixel values, false otherwise.
            continue_stream (bool): True to continue streaming camera feeds, false otherwise
    
        Returns:
            bool: The return value. True for success, False otherwise.
    
        """)

    step_description = sd.S01_DESC.value

    #step_description = "Step 1 - Stream Raw Camera Feed"
    if stream.test:
        # start = popups.yes_no_popup(step_description)
        # start = False
        start = popups.yes_no_popup(sd.S01_DESC.value)

    else:
        # start = uiv.yes_no_quit(step_description)  # Grabs user input for whether or not they want to proceed w/ Step 1.
        start = popups.yes_no_popup(sd.S01_DESC.value)
    display_stream = start
    # display_stream = stream.stepList

    if (stream.histocam_a is None or stream.histocam_b is None) and histogram:  # If use wants to display Histograms
        stream.histocam_a = stream.Histocam()
        stream.histocam_b = stream.Histocam()

    if display_stream is True:
        continue_stream = True
    else:  # We need to at the very least grab some initial frames even if we don't display them.
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames()
        stream.pre_alignment(histogram)

    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames()
        stream.pre_alignment(histogram)
        continue_stream = stream.keep_streaming()

    cv2.destroyAllWindows()  # Upon leaving stream, we want to close any CV2 windows.

    # save to config
    stream.save_config()

    # testing the curve digitizer
    if not stream.test:
        coordsListA, coordsListB = runCurve(stream)

