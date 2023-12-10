from synology_api import filestation
import os
import time
import paramiko
import datetime
import datetime
import requests

def current_time(msg):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(msg, formatted_time)

def webhook_send(content):
    dataInfo = {'content':content}
    URL = 'https://teamroom.nate.com/api/webhook/75bde35a/O2zpHlw3M3OSmQWMAM56w7rV'
    response = requests.post(URL, data=dataInfo)

def webhook_send_admin(content):
    dataInfo = {'content':content}
    URL = 'https://teamroom.nate.com/api/webhook/f3af6d62/l4y0v5TG4fSZWdf94A0drnDb'
    response = requests.post(URL, data=dataInfo)

def upload_file(remote_file):
    # Synology NAS 정보
    nas_host = '10.1.14.53'
    username = '1611006'
    password = 'incar001!'
    # # 업로드할 파일 경로
    local_file_path = 'download/'+remote_file
    current_date = datetime.datetime.now().date()
    current_dir = current_date.strftime("%Y%m")#str(current_date.year)+str(current_date.month)
    nas_file_path = '/SUSURYO_CHECK_DATA/'+current_dir  # 업로드할 NAS 폴더 경로와 파일명

    # Synology NAS 로그인
    nas = filestation.FileStation(nas_host, '5000', username, password)
    #nas = SynologyDSM(nas_host, username, password)
    #nas.get_info()
    # 파일 업로드
    try:
        upload_result = nas.upload_file(nas_file_path, local_file_path, create_parents=True, overwrite=False)
        #print("업로드 결과 : ",upload_result)
        # 결과 출력
        if "Complete" in upload_result:
            print('파일 업로드 성공')
            content = f"""인카디스크에 수수료 검증 데이터 파일 업로드가 완료되었습니다.\n{remote_file}"""
            webhook_send(content)
        else:
            print('파일 업로드 실패')
            content = f"""파일 업로드 실패\n{remote_file}"""
            webhook_send_admin(content)
            os.remove(local_file_path)
    except Exception as e:
        print(f"업로드 중 오류 발생 : {e}")
    finally:
    # Synology NAS 로그아웃
        nas.logout()

def download_new_files(remote_dir, local_dir, hostname, username, password):
    transport = paramiko.Transport((hostname, 22))
    try:
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("SSH 연결, SFTP 객체생성 성공")
        try:
            #sftp.get("/home/project/batchFile/jedo/janggiGeyak/directJanggiGeyak.php", "download/directJanggiGeyak.php")
            #while True:
            remote_files = sftp.listdir(remote_dir)
            download_chk = False
            upload_file_list= ""
            for remote_file in remote_files:
                # remote_path = os.path.join(remote_dir, remote_file)
                # local_path = os.path.join(local_dir, remote_file)
                remote_path = remote_dir+"/"+remote_file
                local_path = local_dir+"/"+remote_file
                #print("remote_path : ", remote_path)
                #print("local_path : ", local_path)
                if remote_file not in os.listdir(local_dir):
                    upload_file_list = upload_file_list+" "+remote_file
                    download_chk = True
                    print(f"Downloading new file: {remote_file}")
                    try:
                        sftp.get(remote_path, local_path)
                        upload_file(remote_file)

                    except Exception as e:
                        print(f"다운로드 실패 {remote_file} : {e}")

            if download_chk == False:
                print("다운로드 할 파일이 없음")

            #time.sleep(600)  # 일정 간격으로 폴더 내용을 체크

        except KeyboardInterrupt:
            print("Download process interrupted.")
        finally:
            sftp.close()
            print("SFTP 연결종료")
    except paramiko.AuthenticationException:
        print("SSH 인증정보 오류")
    except paramiko.SSHException as e:
        print("SSH 연결실패 : ",str(e))
    finally:
        transport.close()
        print("SSH 연결종료")


if __name__ == "__main__":
    #current_date = datetime.datetime.now().date()
    #current_dir = current_date.strftime("%Y%m")
    remote_directory = "/home/project/batchFile/checkData"#"/home/project/batchFile/data"
    local_directory = "download"
    server_hostname = "210.112.120.180"
    server_username = ""
    server_password = ""
    current_time("수수료 검증파일 업로드 작업시작 : ")
    download_new_files(remote_directory, local_directory, server_hostname, server_username, server_password)
    current_time("수수료 검증파일 업로드 작업종료 : ")