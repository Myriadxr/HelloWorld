*** Settings ***
Library  RequestsLibrary
Library  Collections

*** Test Cases ***
test_get_event_list
    ${payload}=     create dictionary  eid=1
    create session  event http://127.0.0.1:8000/api
    ${r}=           get request  event   /get_event_list/   params= ${payload}
    should be equal as strings  ${r.status_code}    200
    log     ${r.json()}
    ${dict}         set variable   ${r.json()}
    # 断言结果
    ${msg}          get from dictionary    ${dict}   message
    should be equal  ${msg}     success
    ${sta}          get from dictionary    ${dict}  status
    ${status}       evaluate    int(200)
    should be equal  ${sta}     ${status}

test_user_sign_success
    create session   sign       http://127.0.0.1:8000/api
    ${headers}=       create dictionary     Content-Type=application/x-www-form-urlencoded
    ${payload}=       create dictionary      eid=11  phone=13122002200
    ${r}=  post request  sign  /user_sign/     data=${payload}  headers=${headers}
    should be equal as strings      ${r.status.code}        200
    log     ${r.json()}
    ${dict}     set variable  ${r.json}
    # 断言结果
    ${msg}      get from dictionary     ${dict}     message
    should be equal  ${msg}     sign success
    ${sta}      get from dictionary     ${dict}     status
    ${status}   EVALUATE  int(200)
    should be equal     ${sta}      ${status}

