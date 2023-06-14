import usocket

socketObject = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
address = ("www.micropython.org", 80)
socketObject.connect(address)
print("\nSetting socket timeout to 5 seconds.")
socketObject.settimeout(5)
print("Calling RECV- this will timeout since no data was requested.\n")
# Call "recv", even though no data has been requested from the host yet,
# meaning none will be received.
try:
    socketObject.recv(1024)
except OSError as error:
    print("Socket timed out!\n")
except:
    print("An error occurred.")
 
# After 5 seconds, there will be an "ETIMEDOUT" OSError, meaning
# the read timed out.  This will not print to the screen since it is caught
# by the "except" block.


print("Setting socket timeout to zero (non-blocking).")
# Set the socket to be non-blocking, by setting the timeout to 0.
socketObject.settimeout(0)
print("Calling RECV- should return immediately with no data.\n")
# Call "recv".
try:
    socketObject.recv(1024)
except OSError:
    print("No data to read!\n")
except:
    print("An error occurred.")
 
# The call will return right away.


print("Setting socket mode to \"Blocking\" meaning it will wait for data.")
# NOTE:  the method "setblocking" is a shorthand way of setting blocking:
# calling "socketObject.setblocking(False)" is shorthand for calling
# "socketObject.settimeout(0)".
# This call will set the socket to be blocking:
socketObject.setblocking(True)
print("Calling RECV with a blocking socket.")
print("This will wait for data, until it either receives it,")
print("the socket times out, or the user cancels the call.\n")
print("This call will time out after approximately 60 seconds.  If you don't")
print("feel like waiting to see that happen, feel free to")
print("press Ctrl-C to cancel the RECV call and return to a prompt...")
# Call "recv".
socketObject.recv(1024)
# The call will not return until the server sends data (which won't happen in
# this case, since none was requested), or the socket times out.