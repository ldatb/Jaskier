import re
import math
import psutil
import platform
import subprocess
import tempfile


def is_valid_url(url):
    """
        Taken from django URL validator
        https://github.com/django/django/blob/master/django/core/validators.py#L65
    """
    ul = '\u00a1-\uffff'  # Unicode letters range (must not be a raw string).

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
    tld_re = (
        r'\.'                                # dot
        r'(?!-)'                             # can't start with a dash
        r'(?:[a-z' + ul + '-]{2,63}'         # domain label
        r'|xn--[a-z0-9]{1,59})'              # or punycode label
        r'(?<!-)'                            # can't end with a dash
        r'\.?'                               # may have a trailing dot
    )
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    regex = re.compile(
        r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
        r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
        r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#][^\s]*)?'  # resource path
        r'\Z', re.IGNORECASE)
    return re.match(regex, url) is not None

def split_to_columns(text):
    lines = text.split("\n")
    max_len = len(max(lines, key=len))  # find longest text in list

    column = []
    halflen = int(math.ceil(len(lines) / 2))
    for x in range(halflen):
        left_line = lines[x]
        len_left_line = len(left_line)
        try:
            right_lane = lines[x + halflen]
        except IndexError:
            right_lane = " "
        len_right_line = len(right_lane)

        # append space to make it equal with longest line
        if len_left_line < max_len or len_right_line < max_len:
            left_line = left_line + " " * (max_len - len_left_line)
            right_lane = right_lane + " " * (max_len - len_right_line)

        per_line = "   ".join([left_line, right_lane])
        column.append(per_line)

    column_text = "\n".join(column)
    return column_text

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def run_sys_info():
    sys_name = f"{platform.system()} - {platform.release()} ({platform.dist()[0]} {platform.dist()[1]} {platform.dist()[2]})"

    total_cpu = psutil.cpu_count()
    cpu_usage_overall = psutil.cpu_percent(interval=1)
    cpu_usage_per_cpu = psutil.cpu_percent(interval=1, percpu=True)

    ram = psutil.virtual_memory()
    total_ram = convert_size(ram.total)
    ram_usage = convert_size(ram.used)
    ram_usage_percent = ram.percent

    disk = psutil.disk_usage('/')
    total_disk = convert_size(disk.total)
    disk_usage = convert_size(disk.used)
    disk_usage_percent = disk.percent

    sys_info_fmt = f"{sys_name} \n"
    sys_info_fmt += f"\nTotal CPU: {total_cpu}\n"
    sys_info_fmt += f"CPU Usage (overall): {cpu_usage_overall}%\n"
    sys_info_fmt += "CPU Usage (per CPU):\n"
    per_cpu_info = ""
    for cpu_num in range(total_cpu):
        new_line = "" if cpu_num == 0 else "\n"
        per_cpu_info += f"{new_line}{' ' * 3}- CPU {cpu_num + 1}: {cpu_usage_per_cpu[cpu_num]}%"
    per_cpu_info = split_to_columns(per_cpu_info)
    sys_info_fmt += per_cpu_info
    sys_info_fmt += f"\n\nTotal RAM: {total_ram}\n"
    sys_info_fmt += f"RAM Usage: {ram_usage} ({ram_usage_percent}%)\n"
    sys_info_fmt += f"\nTotal Disk: {total_disk}\n"
    sys_info_fmt += f"Disk Usage: {disk_usage} ({disk_usage_percent}%)\n"
    return sys_info_fmt

def run_cmd(cmd):
    print(f"Init run cmd: `{cmd}`")
    try:
        cmd_list = cmd.split(" ")
        run = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        run_err = run.stderr.decode('utf-8')
        if run_err != "":
            return False, run_err
        return True, run.stdout.decode('utf-8')
    except Exception as err:
        return False, str(err)

def run_speedtest():
    _, output = run_cmd('speedtest')
    return output


def run_ping(url, times=4):
    cmd = f"ping -c {str(times)} {url}"
    _, output = run_cmd(cmd)
    return output


def create_tempfile(data):
    fp = tempfile.TemporaryFile()
    if type(data) is str:
        data = str.encode(data)
    fp.write(data)
    fp.seek(0)
    file = fp.read()
    fp.close()
    return file