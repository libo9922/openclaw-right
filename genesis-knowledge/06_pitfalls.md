# 06 — 踩坑记录

## 1. Genesis 只能 init 一次

```python
# ❌ 错误：多次 init
gs.init(backend=gs.gpu)
# ... 运行一个场景 ...
gs.init(backend=gs.gpu)  # 报错: Genesis already initialized

# ✅ 正确：一个进程只 init 一次
gs.init(backend=gs.gpu)
scene1 = gs.Scene(...)
# 如果要跑多个场景，用多个进程
```

## 2. 摄像头必须在 build 前添加

```python
# ❌ 错误：build 后添加摄像头
scene.build()
cam = scene.add_camera(...)  # 报错: Scene is already built

# ✅ 正确：先添加摄像头，再 build
cam = scene.add_camera(pos=(1,1,1), lookat=(0,0,0), res=(640,480))
scene.build()
```

## 3. cam.render() 返回 tuple

```python
# ❌ 错误：直接 save
cam.render().save("output.png")  # AttributeError: tuple has no attribute save

# ✅ 正确：取第一个元素
rgb = cam.render()[0]  # numpy array, shape (H, W, 3)
Image.fromarray(rgb).save("output.png")
```

## 4. set_pos 接受 1D Tensor

```python
# ❌ 错误：传 2D numpy
block.set_pos(np.array([[1, 2, 3]]))  # Invalid input shape

# ✅ 正确：传 1D Tensor
block.set_pos(torch.tensor([1, 2, 3], dtype=torch.float32))
```

## 5. MJCF 复杂模型穿模

```
现象：Go2/ANYmal/Spot 加载后直接掉穿地面
原因：Genesis 对 mesh-based 碰撞体支持不完善
解决：只用 Franka 等验证过的模型，或用 GLB 做装饰
```

## 6. pip 安装超时

```
现象：pip install 在国内网络极慢（17KB/s）
解决：用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn <package>
```

## 7. torchcodec ROCm 编译

```
现象：torchcodec 没有 ROCm 预编译包
解决：从源码编译，CPU-only 模式
cmake -DENABLE_CUDA=OFF ...
```

## 8. SmolVLM2 路径 patch

```
现象：lerobot 默认从 HuggingFace 下载 SmolVLM2，网络不通
解决：用 modelscope 下载后，patch lerobot 源码指向本地路径
```

## 9. Training sub-agent 超时

```
现象：sub-agent LLM 请求超时导致训练进程被终止
解决：训练进程是独立的，checkpoint 已保存，可以直接用
教训：长时间任务用 nohup 而不是 sub-agent
```

## 10. 场景实体太多导致极慢

```
现象：64 个地砖让场景 build 超过 5 分钟
解决：减少装饰实体数量，或用纹理贴图代替
```
