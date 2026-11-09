# assets

全站共用的静态资源：logo、图标、favicon、默认占位图。

单篇文档的配图**不放这里**，放在各自同级的 `images/` 目录下。判断标准：这张图是否被三个以上不同目录的文档引用？是，才放这里。

```
assets/
├─ logo-wyn.svg
├─ logo-grapecity.svg
├─ favicon.ico
└─ placeholder-dashboard.png
```

引用时从文档所在位置算相对路径，例如 `docs/01-product/README.md` 引用 logo 写 `../../assets/logo-wyn.svg`。
