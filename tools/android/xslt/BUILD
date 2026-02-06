load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@rules_python//python:py_binary.bzl", "py_binary")

exports_files(["add_g3itr.xslt"])

# sh_binary(
#     name = "xslt",
#     srcs = ["xslt.sh"],
#     visibility = ["//visibility:public"],
# )

py_binary(
    name = "xslt",
    srcs = ["xslt.py"],
    visibility = ["//visibility:public"],
)
