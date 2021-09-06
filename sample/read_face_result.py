import time
faceresult_path = "/home/pi/Face-Recognition/face.result"

now_time = time.time()
with open(faceresult_path, 'r') as f:
	lines = f.readlines()
	f_name = lines[0].strip()
	f_time = float(lines[1].strip())

	tm = time.gmtime(f_time)
	print("{0}년 {1}월 {2}일, {3}시 {4}분 {5}초".format(
				tm.tm_year,
				tm.tm_mon,
				tm.tm_mday,
				tm.tm_hour,
				tm.tm_min,
				tm.tm_sec))
	print("시간차이 : %d" % int(now_time - f_time))
	print("사용자명 : %r" % f_name)

