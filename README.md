<h1 align="center">django-vue-suit arrives!</h1>

<p align="center">
  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />
  <img src="https://img.shields.io/badge/language-python3-blue.svg?cacheSeconds=2592000" />
</p>

### 🏠 [个人小栈](https://ryuchen.github.io/)

    > 未来更新的说明会刊登在这里，并且会不定时分享部分内容和心得

### 📎 项目说明:

  * django-vue-suit 是一套正在开发的，后续将支持开发者，创建一套完整的前中后台都有的项目的构建脚手架，能够帮助用户通过简单的构建 models 层面就可以定义最终的前中后台展示效果 ~ 项目由 django + ant-design-vue 构成，并没有使用 node 作为开发环境，作为纯后端应用存在 ~
  * vueSuit 是核心源代码模块，参照了 django.contrib.admin 模块和 django.forms 模块，创建了各自相对应的 vueAdmin 和 vueForms 模块，并且提供了一套完整的 vuePacks 模块使用 ~
    + vueAdmin 是替换 django admin 模块，提供了完整的原先 django admin 功能，同时还提供了一套完整的拓展 UI 使用，方便用户自定义一些展示效果 ~
    + vueForms 是替换 django forms 模块，提供了完整的原先 django forms 功能，同时还提供了一套 ant-design-vue forms 的配置功能，实现了由后台 python 代码控制前台 form 表单的基本校验功能 ~
    + vuePacks 是完全新建的模块，使用方法会参照 django admin 的使用，提供一套注册和定义展示的机制，让开发者仅通过定义一个简单的 python 脚本就实现对于后台数据的展示，实现一套完整的前台应用 ~
    
### 📝 待办清单:

vueAdmin:
  * [ ] 摘抄 django contrib admin 模块代码过来，去除相应依赖
  * [ ] 重构 相应路由，去除掉不需要的路由支持
  * [ ] 重构 整个 admin template 的 skeleton，引入 ant design vue 的 css 和 js 脚本作为展示效果
  * [ ] 新增 Dashboard 页面添加到项目中
  * [ ] 
  
vueForms:
  * [ ] 摘抄 django contrib admin 模块代码过来，去除相应依赖
  * [ ] 重构 基本的 widget 展示效果，替换为 ant design vue 的 component
  * [ ] 增加 通过定义 models fields 使用的 widgets 展示时的 vttrs 参数，扩展对于最终 forms 的表单验证功能
  
vuePacks:
  * [ ] 待开发

vuePlugins:
  * [ ] 增加 vuePlugins 模块，提供第三方拓展功能，因为较为底层的重构了 django admin 和 django forms 模块，导致一些跟 admin UI 有关 django packages 不再生效，不过后续会提供拓展支持，并且将转化一些常用的 packages 过来 ~
  * [ ] To support plugins:
    
       * [ ] django-import-export
     
   
### 📖 安装说明:

```shell
  
  pip install -U django-vue-suit
  
```  

```python 
  # 在 settings.py 文件中 引入该模块
  
  INSTALLED_APPS = [
    ...
    'vueSuit.vueAdmin',
    'vueSuit.vueForms',
    'vueSuit.vuePacks',
    ...
  ]

```

### 📷 页面展示:

   > 待添加



### 👤 作者介绍:

Ryuchen ( 陈 浩 )

* Github: [https://github.com/Ryuchen](https://github.com/Ryuchen)
* Email: [chenhaom1993@hotmail.com](chenhaom1993@hotmail.com)
* QQ: 455480366
* 微信: Chen_laws

Nameplace ( 虚位以待 )

### ⭐ 渴望支持: 

如果你想继续观察 django-vue-suit 接下来的走向，请给我们一个 ⭐ 这是对于我们最大的鼓励。
此外，如果你觉得 django-vue-suit 对你有帮助，你可以赞助我们一杯咖啡，鼓励我们继续开发维护下去。

| **微信**                         | **支付宝**                           |
| ------------------------------- | ----------------------------------- |
|<p align="center">![扫码赞助](https://github.com/Ryuchen/Panda-Sandbox/raw/master/docs/sponsor/wechat.jpg)</p>|<p align="center">![扫码赞助](https://github.com/Ryuchen/Panda-Sandbox/raw/master/docs/sponsor/alipay.jpg)</p>|

### 🤝 贡献源码:

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/Ryuchen/Bistu/issues).
