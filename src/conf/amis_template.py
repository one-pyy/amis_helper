AMIS_TEMPLATE="""
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8"/>
  <title>{%title%}</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <meta
      name="viewport"
      content="width=device-width, initial-scale=1, maximum-scale=1"
  />
  <meta http-equiv="X-UA-Compatible" content="IE=Edge"/>
  <link rel="stylesheet" href="{%sdk_path%}/sdk.css"/>
  <link rel="stylesheet" href="{%sdk_path%}/helper.css"/>
  <link rel="stylesheet" href="{%sdk_path%}/iconfont.css"/>
  <!-- 这是默认主题所需的，如果是其他主题则不需要 -->
  <!-- 从 1.1.0 开始 sdk.css 将不支持 IE 11，如果要支持 IE11 请引用这个 css，并把前面那个删了 -->
  <!-- <link rel="stylesheet" href="{%sdk_path%}/sdk-ie11.css" /> -->
  <!-- 不过 amis 开发团队几乎没测试过 IE 11 下的效果，所以可能有细节功能用不了，如果发现请报 issue -->
  <style>
      html,
      body,
      .app-wrapper {
        position: relative;
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
      }
  </style>
</head>
<body>
<div id="root" class="app-wrapper"></div>
<script src="{%sdk_path%}/sdk.js"></script>
<script type="text/javascript">
(function () {
  let amis = amisRequire('amis/embed');
  let amisLib = amisRequire('amis');
  // 通过替换下面这个配置来生成不同页面
  let amisJSON = {%json%};
  let amisScoped = amis.embed('#root', amisJSON);
})();
</script>
</body>
</html>
"""

AMIS_EDITOR_CODE="AMIS页面CRUD", r"""
{
  "type": "tabs",
  "id": "u:6b9ae22bcb9e",
  "tabs": [
    {
      "title": "AMIS pages CRUD",
      "body": [
        {
          "type": "form",
          "title": "",
          "body": [
            {
              "type": "select",
              "label": "路径",
              "name": "path",
              "id": "u:8722b967366f",
              "required": true,
              "clearable": false,
              "source": "get:/amis/path",
              "editable": true,
              "creatable": true,
              "removable": true,
              "createBtnLabel": "新增路径",
              "editApi": {
                "method": "patch",
                "url": "/amis/path",
                "data": {
                  "origin": "${value}",
                  "replace_as": "${label}"
                },
                "dataType": "json",
                "requestAdaptor": ""
              },
              "checkAll": false,
              "multiple": false,
              "joinValues": true,
              "deleteApi": {
                "method": "delete",
                "url": "/amis/path",
                "data": {
                  "path": "${value}"
                },
                "dataType": "json"
              },
              "submitOnChange": false,
              "validateApi": "",
              "validateOnChange": true,
              "autoComplete": "",
              "validationErrors": {},
              "addApi": {
                "method": "post",
                "url": "/amis/path",
                "data": {
                  "path": "${label}"
                },
                "dataType": "json"
              },
              "autoFill": {
                "title": "${paths[label].title}",
                "json": "${paths[label].json}"
              },
              "addControls": {
                "type": "dialog",
                "body": [
                  {
                    "type": "input-text",
                    "name": "label",
                    "label": false,
                    "placeholder": "请输入名称",
                    "autoComplete": false
                  }
                ],
                "closeOnEsc": true,
                "closeOnOutside": true,
                "showCloseButton": true
              },
              "onEvent": {
                "change": {
                  "weight": 0,
                  "actions": [
                    {
                      "componentId": "u:9a9d507145aa",
                      "actionType": "reload",
                      "dataMergeMode": "merge"
                    }
                  ]
                }
              },
              "size": "full"
            },
            {
              "type": "input-text",
              "label": "标题",
              "name": "title",
              "id": "u:9a9d507145aa",
              "required": true,
              "checkAll": false,
              "autoComplete": false,
              "options": [],
              "addOn": null,
              "showCounter": false
            },
            {
              "type": "editor",
              "label": "JSON",
              "name": "json",
              "id": "u:ac9f93e6e14e",
              "size": "xl",
              "required": true,
              "options": {
                "tabSize": 2
              },
              "language": "json"
            }
          ],
          "api": {
            "method": "post",
            "url": "/amis/set_pages",
            "data": null,
            "dataType": "json",
            "replaceData": false
          },
          "id": "u:98f14e7b6866",
          "wrapWithPanel": true,
          "submitText": "提交",
          "persistData": false,
          "debug": false,
          "checkAll": false,
          "initApi": "/amis/all_pages",
          "actions": [
            {
              "type": "submit",
              "label": "提交",
              "actionType": "submit",
              "dialog": {
                "title": "系统提示",
                "body": "对你点击了"
              },
              "id": "u:bfe7199fd833",
              "level": "primary",
              "reload": "forms"
            }
          ],
          "name": "forms",
          "silentPolling": true,
          "stopAutoRefreshWhen": "oldPath==path",
          "messages": {
            "fetchFailed": "",
            "saveSuccess": "成功",
            "saveFailed": "失败"
          },
          "feat": "Edit"
        }
      ],
      "id": "u:154e8f522e97",
      "hash": "amis"
    },
    {
      "title": "js code escape",
      "body": [
        {
          "id": "u:a2d4f6dfb92c",
          "type": "form",
          "title": "",
          "mode": "horizontal",
          "dsType": "api",
          "feat": "Insert",
          "body": [
            {
              "type": "editor",
              "label": "js代码",
              "name": "js_code",
              "id": "u:92557c2f8314",
              "language": "javascript",
              "onEvent": {
                "change": {
                  "weight": 0,
                  "actions": [
                    {
                      "actionType": "setValue",
                      "componentId": "u:f38e2c69e26b",
                      "args": {
                        "value": "${REPLACE(js_code, \"\\n\",\"\\\\n\")}"
                      },
                      "ignoreError": false
                    }
                  ]
                }
              },
              "resetValue": "${bbb}",
              "mode": "normal"
            },
            {
              "type": "textarea",
              "label": "转义后js代码",
              "name": "js_code_after_escape",
              "id": "u:f38e2c69e26b",
              "minRows": 1,
              "maxRows": 20,
              "trimContents": false,
              "showCounter": true,
              "onEvent": {},
              "resetValue": "${aaa}",
              "value": "",
              "mode": "normal"
            }
          ],
          "actions": [],
          "resetAfterSubmit": true
        }
      ],
      "id": "u:bc56dad5adb7"
    }
  ],
  "tabsMode": "chrome"
}"""

HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'DNT': '1',
  'Pragma': 'no-cache',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
  'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
}