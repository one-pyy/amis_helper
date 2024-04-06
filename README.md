# amis_helper

方便部署amis的小玩意, 适用于fastapi

部署amis代码后访问"/admin", 默认有超管root/root和管理员admin/admin; 用了fastapi_amis_auth来做鉴权, fastapi_amis_admin来布置后端。

配置文件在src/conf, 记得上线改jwt_secret为空或长随机数

如果打不开就换个cdn, 里面放了一些cdn, 如果不能用的话请自行下载amis-sdk放在src/amis_sdk

登录后有一个amis CRUD, 你可以提交自己的amis代码后在/amis/pages/[your path]直接访问, 如果是管理页面, 也可以用IFrameAdmin加到管理页面 / 用PageAdmin的page.model_validate_json([your json])

> 她走进了我的生活，就像是那道灿烂的阳光，照亮了我曾经阴暗的心灵。她带给我的不仅仅是温暖，更是希望。她是那种善良、美好、充满生机的存在，使我世界的色彩不再是黑与白，而是有了色彩。她是那明亮的星星，照亮了我的黑夜。她的出现是命运的安排，使死气沉沉的生活充满了意义，她给了我发现美的眼睛，使我看到了从未有过的另一个星空。
>
> 是的，她就是[amis_helper](https://github.com/one-pyy/amis_helper)，搭载极致奢华终端log，使你可以看到用户的一举一动，成为窥屏的神！

