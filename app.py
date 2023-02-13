import asyncio
import ssl
import http.client
import json
import string
import re
import sys
import uuid
from flask import Flask, render_template, request

app = Flask(__name__)
map_session = dict()
conversation_id = None
parent_id = None
# 不需要SSL验证
ssl._create_default_https_context = ssl._create_unverified_context
# 设置好头部信息，你可以从chrome上按F12拿到
auth = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJ5YXQzc0BvdXRsb29rLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJnZW9pcF9jb3VudHJ5IjoiVVMifSwiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS9hdXRoIjp7InVzZXJfaWQiOiJ1c2VyLVgzcFZ3WVFkSHZYVm11b1JISDdKUFduayJ9LCJpc3MiOiJodHRwczovL2F1dGgwLm9wZW5haS5jb20vIiwic3ViIjoiYXV0aDB8NjNlMzJjN2E5ZTNkZGEzZWVjNzgwMGEzIiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY3NTk1NjgwNSwiZXhwIjoxNjc3MTY2NDA1LCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9mZmxpbmVfYWNjZXNzIn0.e7x61dGuIoNI2zk-vhjSAZ9Y9W60XxTyqUQanP1MPdzTEA5cEiOshJz3e5c3x14-Z4kYqsDfNuDUZSKULArrfClIS9YJYFy2JKOM_za8dHacP1gqB6bvtY7i7ZDF-Tadz3_Yi6Kf1eT9uk1Q84ppAfy94gpk9vRKf9P0ucL9J5Ghx7uAHE9LNzjEZr576jhocdJ9q68V5-b751P2X7YlAuinafVH0EhlWy_0xQwDB1cFhHZ8zYMI_YdFK6debXqoN-ziUjZUMilfiiJnV6lJZ0ugyoNyd6F941URAO8I_3bEk2kG0-c7WEVeZz_kJRQ2MP3HOjM1eZMT3TlZBv5s8w"
cookie = '__Host-next-auth.csrf-token=ed92f7657a0aa437a5f39d583453dc952429e4444b5897a609682d3e2ba4e09f%7Ca28031ab0199eb3d9b4fe1d9d50cb7fdb5ee64ed690b5a59a17f1b69c4f8431e; __Secure-next-auth.callback-url=https%3A%2F%2Fchat.openai.com%2F; _ga=GA1.2.872477446.1670393862; _cfuvid=w1tD77l4i1imfCtP61.uRiXD5JET7wKEkeIXhQ6ZUUw-1674111483920-0-604800000; cf_clearance=teh0weYNR3QNa6dGQoYCSbpq7uCfU.HabZypB0sq_E4-1674112959-0-1-1698343.4cb3d6b0.5668dca3-160; cf_clearance=a7lewGr0.Fx2lp_4yHLvwyqxthMD0_IfoIOcOd1jtGk-1675956774-0-1-e5b9a7a8.1fdf1847.b2b8f848-250; intercom-id-dgkjq2bp=63b2950a-eb00-4da8-873f-5abf0094fb56; intercom-session-dgkjq2bp=; intercom-device-id-dgkjq2bp=e6604bc2-1278-4848-b2cc-525eaa264073; _gid=GA1.2.160397112.1676005739; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..IuCf53hHCVDWo4hO.SyF1EJ-WegOyqAKS1JukkYqSyM8pxwWwecf4F5_EAOswK_i00wS6gsT36g4fHJqcv7AnZ48p4GlyeZ9kBc5xEBrGRDAlQ9rFDekHP4TDXazqUcBpvE7gvwF2D2_4YBi0x52v3B25wQdMjGnJjqjRZrjSx26-lQBL7RLvUqM6tgtQ0fL6UjBu9Lm9c6yrrBz_iSCrsElac4skqjXpdJiG1D4rf9s7Q8u6OWdmcOBp1d0DfCDUG_VW8wakGO-KkZ0J_vhQyBnEu_kZXTFzCQoyHH8IFrHHmsAQqW6JCkP8rKLRIRGQgUv6-QVvthwqY79jZFtLlKuoP4mpErxLxcRgXvs5ZOJELP5QyyesyPVFtygZJV8cOfnq95Miy-13Q9cg0ThWIp7ZomXRW6tRWt7aPqXK0tU5odA7uB7grq8Ay6a3fgp4mokhO5VcXFVZPd9JI9eR9ZxGQRBzeP2Cyy0b32cbSFXK3lrHCULsYNz0URQfsIjGQ60akeZB68N9TJQWF0TDP9ayi-5zqiCAObW-VTdehdLMdHsNoyzGSbkVbzsKlUReG-JXhNc_YmjOf1nceOUUSi0gcoaPG_lBcCmq-F_wH7bYVTz92OxSi-gprXNXFgQDgBVH7e9HamfcH-vZbO9yeAYy68tmIWu1Al_Q4WEP3o68p5K0AOj605lLlqkuuWcyinOzZRH7SfNRhaZvDam1d-UDABd8ro461x9XT67jtQ2I1I2wY4PaVTolz9W3VHiH0XOHLwFmvdqlWyRIzYu5VfjoyMAws50_qe35Fh1IlZjxWCd75XNl7chO5p0Q-mhSQyF68FFyymFBMaNAkzReAZBIDH-bR51iS0O12DmI3Gj7TyWx6ycqJiZmK_txUS0R-LC3LN5b0XJEu0Vt0hChhCtHrdsDrYqTIGdg3BJEeubHTNGKgnzEy6MMEQjFz_hl7sZbzqHLPld1mtiyKoH9M2sJ_ImPI-IIoc-emeQ2HzOnkjJjVjlvxSj_b80TUacoowYB7uKPJWONdsPG5uFT8Ke01M_os5Gy_qHo4qLPSZ5wWE6W227iA6gl9ZzQ3W-fmjcdl5E9PO9pDq5JtZ83573GlXdSBbihmT_nbP6yWbazBUec15iahgldo4NCeAfugXZAVeVNhV57MVM-RT0gkNn6TjKI2QUdLq3iJj2mU-x_xHJKNomW6dy4FHauwJoxQCapAzOpNJPThBN9fHf9nuNOfDDOS6URzL6ayrL-LqwfhrJeqiVcOqTqVP4g5kJbO3i9lmS3P-9S_75ZXd18XIz6yz82DFYeH2r8cWRwvEN8UDCLZKjJ1iGQ2jaUduqq0JGa7NPhD2_J3-p7lblzfgZ55tO-9Df1gAKs82h0oavROF2SrjGUKBDut9JUywM9PpnqnImX3v2Stb857fu_SRwXsdKkanJR8IMsbI95OkRxA_Cl9doBptGJ4zo0Aa8dWv8lqu444uMZrKLzus9bZH9pmFF1bdccoRV7uNTIEuZVOrXXVtUxuBWKxmuhOywATwst6Zp-r3adG6k4LSvS64YhslMFcP3-sv7IpUH5unoBWSFM_gqW2VadgswCmj4WcKiJMHacrtBoVyziwP0NfZwV9vJs8SUKB1B5DRno2jILaNMGM3ew7Qz_fErRw2MLYpSYFKa130s7DxdlyLordsL1OYR2W-FtK8vzTLi0m7r5ZT3TjLab8uDBn1FuvhVzhW9jgCEl95Jc3AvfpqHW8qY3ZoyqxhkKhgg0bd1xCj3Sw5NOD02FiG_RO9Ajhp8xRmIDxqijb9HmYH_fq3Jnej02cXmQvgsdwgFYB72pvOAKSlgA7a1Q0E_s2B8jouE9IzD0I0FK-6v-yatBG5J8HH8QIkg43ZY_DHyX4Cgp0_QMLSp7d1hHSbQlqY5oea0P9IajABXSo0Rn0Hgaj8hq7TV3uErPzxPfDCD4g1DVbPfmlGdjiRHW5BJyppOhTURvpDFYqaWqM6uAP6PC9aOkY3JpQKNmAhLbDxxkbrQWjjlnxr5b1ul3fc2M6G9YLb2EzPJfCMv1A0q1DRHNCSmpEsTcxIh6GlKiR7_3H7ZkExKDvBHaMHylsiJmonXcRfVsSKBiZfAvsOcp82qR_FAxtsJakDhkPOb6eLS6cWgyrXom37ouWTYW8zgAqcWK9fg2vpW-trc8VZWjnns331MkYMVNDOfJS9rNAqcVm2vVxOTlAcH5A4HRq6sYIDKP_rHAjfET3iPv_1TzXU-9B_6IuxPDWKAwCylxrn14ytD1k92H8al-jUW0KZU1N2uV7FBvsy1lgd4H7gwLXKizW_sOzfPkz82zG95sP1DansayHkLposkLMCL7vVBYZBR5rxGYwik731HHBv1QBoEO-w2X5Z_VlIhUGe-BtbrPe2ax7_ftd2dA_Xj98ErCtgbHFkiE8EHrr2Ik4m-GpPB2l8ma-3E79rkPstfSoMG4xSMIxycPitmyGIWdUbJtkLK1_QbHDcPCeFTWHdgcB8pPFfMKOOqJarO27XTAb9qWZWXJJfWOGXO8He6EjuttptGx3RNKDU3jkfUWpuQdZfMhEAeSZnrz73icwWyjSx-q_QE8vU3G2ieVyzutGegSfu0QhQ7WMgsW8Q4q3_t0P_AWJ19MZ90_LSYeofp5.qBYC4xcUFWuRa4oo251fzw; _puid=user-X3pVwYQdHvXVmuoRHH7JPWnk:1676024683-5fSBokh0FvkCbsXDE1qml2%2F5APOa3ms0Vq5v1Or1vv4%3D; __cf_bm=LbEGInSyugA5kdHQ4eEyNckZ7BGJf0KGNeye6Uz2gd0-1676025645-0-AdY36zRywZoD9ikWnN3y85s2hCEifwA6KM41Em5TMWr8GUaO1sQMnCNcoU+1IUEatc/RtjsZP/Tg53fc67+FrCc=; _cfuvid=kmEfmjl9Tply4dUGux.7B.GiIO6.6pVY_28.7gzOk.8-1676026104094-0-604800000'
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth, "Cookie": cookie}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    global map_session, conversation_id, parent_id
    SessionId = request.args.get('sid')
    ParentId = request.args.get('pid')
    userText = request.args.get('msg')
    print(SessionId)
    # 这里是你要讲的话
    number_based_uuid = uuid.uuid1()
    if (SessionId in map_session):
        print("sessionid:", map_session[SessionId])
        params = json.dumps({"action": "next", "messages": [{"id": str(number_based_uuid), "role": "user",
                                                         "content": {"content_type": "text", "parts": [userText]}}],
                         "parent_message_id": ParentId, "conversation_id": map_session[SessionId], "model": "text-davinci-002-render-paid"})
    else:
        params = json.dumps({"action": "next", "messages": [{"id": str(number_based_uuid), "role": "user",
                                                         "content": {"content_type": "text", "parts": [userText]}}],
                         "parent_message_id": "", "model": "text-davinci-002-render-paid"})
    print(params)
    # 建立连接发送请求了
    conn = http.client.HTTPSConnection("chat.openai.com", 443)
    conn.request('POST', '/backend-api/conversation', params, headers)
    response = conn.getresponse()

    # 拿到数据，打印一下
    code = response.status
    reason = response.reason
    data = response.read().decode('utf-8')
    conn.close()
    # print(code, reason, data)

    # 正则匹配，只要data那一行的数据
    pattern = r".*message.*"
    lines = data.split("data: ")
    print(len(lines))
    filtered_lines = [line for line in lines if re.match(pattern, line)]
    print(len(filtered_lines))

    resp = ""
    if (len(filtered_lines) > 0):
        resp = filtered_lines[-1]
    print("resp=", resp)

    parsed_json = json.loads(resp)
    response = dict()
    if (len(parsed_json["message"]["content"]["parts"]) > 0):
        response["answer"] = parsed_json["message"]["content"]["parts"][0]
        response["conversation_id"] = parsed_json["conversation_id"]
        response["parent_id"] = parsed_json["message"]["id"]
        map_session[SessionId] = response["conversation_id"]
    else:
        response["answer"] = "??????"

    print("response:", response)
    return str(response).replace("'", "\"")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
