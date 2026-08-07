---
title: "生产级 Go 服务开发包推荐"
weight: 5
type: docs
bookToC: true
slug: "go-production-packages"
aliases:
  - "/docs/blog/生产级Go服务开发包推荐/"
  - "/s/bile/"
shortlink: "bile"
---

# 生产级 Go 服务开发包推荐

本文整理了生产级 Go 服务端开发中常用的第三方包，并说明它们的适用场景、优势与选型取舍。

> 本文译自 winterjung 的 [Go Package Recommendations for Production Server Development](https://www.winterjung.dev/en/golang-pkgs-for-production-server/)，原文发布于 2026 年 3 月 4 日。


本文汇总了作者在使用 Go 开发服务端时最常用、也最实用的一批**第三方包**。Go 标准库里当然也有很多可靠且设计精良的包，例如 [`net/http/httptest`](https://pkg.go.dev/net/http/httptest) 和 [`crypto/rand`](https://pkg.go.dev/crypto/rand)，但本文只讨论第三方包。


## [stretchr/testify](https://github.com/stretchr/testify)

```go
func TestSomething(t *testing.T) {
  assert.Equal(t, expected, got, "they should be equal")
  assert.NoError(t, err)
  assert.Len(t, result, 1)
  assert.JSONEq(t, `{"name": "hello"}`, msg)
}
```

> 一套与标准库配合良好的常用断言和 Mock 工具集。

- 它让 Go 原本就很强的测试能力更加丰富，也让测试代码写起来更轻松。
  - 可以用 `assert.Equal(t, expected, got)` 代替 `if got != expected { t.Errorf("...") }`，可读性更好。
- 最常用的是 [assert](https://pkg.go.dev/github.com/stretchr/testify/assert) 和 [require](https://pkg.go.dev/github.com/stretchr/testify/require)。
  - `require` 与 `assert` 几乎相同，区别在于断言失败时会立即终止当前测试。
  - 如果你从其他语言转到 Go，可能会觉得 `require` 的行为更加熟悉。
  - 使用 `assert` 时，同一测试中的后续断言仍会继续执行，因此一次能看到多个失败点，对调试很有帮助。
  - 在 given/when/then 结构中，`require` 很适合 given 阶段，例如客户端初始化以及其他必须成功的准备步骤。
- testify 提供了大量断言函数，值得花时间了解并充分利用。
- [suite 包主要面向习惯面向对象语言的开发者](https://github.com/stretchr/testify#suite-package)。刚开始使用时，只用 `assert` 包就完全足够。
  - 需要注意，截至 v1，suite 仍不支持并行测试。
- 它也很适合搭配 [Antonboom/testifylint](https://github.com/Antonboom/testifylint) 使用。

## [rs/zerolog](https://github.com/rs/zerolog) 与 [sirupsen/logrus](https://github.com/sirupsen/logrus)

```go
import (
    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
    "github.com/rs/zerolog/pkgerrors"
)

func main() {
    zerolog.ErrorStackMarshaler = pkgerrors.MarshalStack
    // ...
    log.Error().Stack().Err(err).Msg("failed to insert row to db")
}
```

> rs/zerolog：零分配的 JSON 日志库。

```go
import (
    log "github.com/sirupsen/logrus"
)

func main() {
    log.WithFields(log.Fields{
        "animal": "walrus",
    }).Info("A walrus appears")
}
```

> sirupsen/logrus：适用于 Go 的结构化、可插拔日志库。

- 两个日志包都支持携带上下文的结构化日志。
  - 服务端日志始终建议采用单行 JSON 格式。
- zerolog 的性能据说更好，但两者都是可以用于生产环境的可靠选择。
  - logrus 已进入维护模式，不过它的功能已经很完善，并且仍会接收安全补丁。
  - 就个人体验而言，logrus 的 `WithFields` 方法让它比 zerolog 更顺手。
- 两者都支持 Hook，很适合在写日志的同时记录指标或注入堆栈信息。
- Go 1.21 起进入标准库的 `log/slog` 也是值得考虑的替代方案。
  - [Structured Logging with slog - The Go Programming Language](https://go.dev/blog/slog)
  - [Logging in Go with Slog: The Ultimate Guide](https://betterstack.com/community/guides/logging/logging-in-go/)

## [pkg/errors](https://github.com/pkg/errors)

```go
resp, err := userSvc.GetUser(ctx, &GetUserRequest{...})
if err != nil {
    return errors.Wrap(err, "user.GetUser")
}
```

> 简单的错误处理基础组件。

- 可以给错误补充上下文和堆栈信息。
- 它诞生于 Go 1.13 之前标准库 `errors` 功能不足的时期。即使后来标准库[加入了 `Unwrap`、`Is` 和 `As`](https://go.dev/blog/go1.13-errors)，但它仍然是通用选择。

## [hashicorp/go-multierror](https://github.com/hashicorp/go-multierror)

```go
var errs *multierror.Error
if err := step1(); err != nil {
    errs = multierror.Append(errs, err)
}
if err := step2(); err != nil {
    errs = multierror.Append(errs, err)
}
return errs.ErrorOrNil()
// Output:
// 2 errors occurred:
//     * error 1
//     * error 2
```

> 用一个错误表示一组错误的 Go 包。

- 作者经常在校验配置或请求时使用它，因为它可以一次返回更完整的错误信息。
- 包内的 `multierror.Group` 也很实用，可以并发启动多个 goroutine，再收集每个 goroutine 的错误。
- 类似的选择还有准标准库包 [golang.org/x/sync/errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)。
  - 使用 errgroup 时，一个 goroutine 返回错误会将错误传播给其他 goroutine，并取消它们的工作，因此要根据场景选择。
  - 相比之下，multierror 会让所有 goroutine 执行完毕，再合并它们的错误。

## [samber/lo](https://github.com/samber/lo)

```go
names := lo.Uniq([]string{"Samuel", "John", "Samuel"})
// []string{"Samuel", "John"}
```

> 基于 Go 1.18+ 泛型、风格类似 Lodash 的 Go 工具库，提供 map、filter、contains、find 等能力。

- 它利用 Go 1.18+ 的泛型减少样板代码，同时不会带来性能损失。
- 作者个人最常用的是 `Map`、`SliceToMap` 和 `Keys`。
  - Go 1.21 引入的 [maps](https://pkg.go.dev/maps) 和 [slices](https://pkg.go.dev/slices) 标准库已经覆盖了不少相同功能，也值得先看看。
- 同一维护者还开发了用于依赖注入的 [samber/do](https://github.com/samber/do) 和用于单子类型的 [samber/mo](https://github.com/samber/mo)。但它们不符合作者偏好的 Go 代码风格，所以最终没有采用。

## [shopspring/decimal](https://github.com/shopspring/decimal)

```go
func main() {
    price, err := decimal.NewFromString("136.02")
    quantity := decimal.NewFromInt(3)
    subtotal := price.Mul(quantity)

    fmt.Println("Subtotal:", subtotal) // Subtotal: 408.06
}
```

> Go 的任意精度定点十进制数实现。

- 另一个同类包是 [ericlagergren/decimal](https://github.com/ericlagergren/decimal)，但 `shopspring/decimal` 用起来明显更顺手。
- 它与 ORM 库中的 decimal 类型能够很好地对应。
- 如果关注性能，建议对 README 中提到的其他包进行基准测试后再选择。

## [dgraph-io/ristretto](https://github.com/dgraph-io/ristretto)

```go
func main() {
    cache, _ := ristretto.NewCache(&ristretto.Config[string, string]{
        NumCounters: 1e7,     // 要跟踪访问频率的 key 数量（1000 万）
        MaxCost:     1 << 30, // 缓存的最大成本（1 GB）
        BufferItems: 64,      // 每个 Get 缓冲区包含的 key 数量
    })
    cache.Set("key", "value", 1)
    value, found := cache.Get("key")
    fmt.Println(value)
}
```

> 高性能、有内存上限的 Go 缓存。

- 当生产环境需要高性能的进程内本地缓存时，它是一个可靠选择。
  - 如果想了解这个包的设计背景和重点，可以阅读 [Introducing Ristretto](https://web.archive.org/web/20250207211235/https://dgraph.io/blog/post/introducing-ristretto-high-perf-go-cache/)。
  - 最优配置会随场景变化，建议结合指标和基准测试确定参数。
- 它支持泛型。
  - [patrickmn/go-cache](https://github.com/patrickmn/go-cache) 不支持泛型，而且已经停止维护，因此不推荐使用。
- 如果需要在高流量环境下进一步调优，可以研究 [creativecreature/sturdyc](https://github.com/creativecreature/sturdyc) 和 [maypok86/otter](https://github.com/maypok86/otter)。
  - 想深入了解本地缓存性能的关键因素，可以阅读 [Writing a very fast cache service with millions of entries in Go](https://blog.allegro.tech/2016/03/writing-fast-cache-service-in-go.html)。

## [coocood/freecache](https://github.com/coocood/freecache)

```go
cacheSize := 100 * 1024 * 1024 // 100 MB
cache := freecache.NewCache(cacheSize)

cache.Set([]byte("key"), []byte("value"), 60) // TTL 为 60 秒
value, err := cache.Get([]byte("key"))
```

> GC 开销为零的 Go 缓存库。

- 这是一个尽量降低 GC 开销的进程内本地缓存。无论缓存多少条目，它都只使用 512 个指针。
- 它会单独分配一块内存作为环形缓冲区，因此 GC 在标记清扫时需要扫描的对象更少。
- 但它要求 key 和 value 都序列化成 `[]byte`。如果项目已经在使用 protobuf，迁移成本会比较低。
  - 当堆内存的 GC 开销高于序列化开销时，它最有价值。
- 如果说 ristretto 是通用本地缓存，那么 freecache 更适合需要关注 GC 调优的大规模缓存。

## [volatiletech/sqlboiler](https://github.com/volatiletech/sqlboiler)

```go
import (
    "github.com/volatiletech/sqlboiler/v4"
)

func main() {
    users, err := model.Users().All(ctx, db)
    token, err := model.Tokens(
        model.TokenWhere.AccessToken.EQ(accessToken),
    ).One(ctx, db)

    token.Update(ctx, db, boil.Whitelist(
        model.TokenColumns.AccessToken,
        model.TokenColumns.AccessTokenExpiredAt,
    ))
}
```

> 根据数据库 Schema 生成定制的 Go ORM。

- 它不要求在 Go 代码中维护数据库模型，而是根据已有数据库 Schema 生成对应的 Go 代码。
- 构造查询的体验也很好：不必手写原始字符串，可以直接使用已经生成的类型。
- 当然还有其他选择。以个人体验来说，[sqlc-dev/sqlc](https://github.com/sqlc-dev/sqlc) 使用起来比较繁琐；如果符合你的偏好，也可以尝试 [go-gorm/gorm](https://github.com/go-gorm/gorm)。
- 不过，sqlboiler 已经[进入维护模式](https://github.com/aarondl/sqlboiler#maintenance-mode)，目前只进行安全补丁等最低限度的维护，新项目值得优先评估替代方案。
  - [sqlc-dev/sqlc](https://github.com/sqlc-dev/sqlc) 根据 SQL 查询生成类型安全代码；[stephenafamo/bob](https://github.com/stephenafamo/bob) 则是类型安全的查询构造器，更接近 sqlboiler 的精神继任者。
  - 参考：[Golang ORM, Which One Is Good?](https://blog.billo.io/devposts/go_orm_recommandation/)

## [DATA-DOG/go-sqlmock](https://github.com/DATA-DOG/go-sqlmock)

```go
func TestShouldUpdateStats(t *testing.T) {
    db, mockDB, err := sqlmock.New()
    require.NoError(t, err)
    t.Cleanup(db.Close)

    mockDB.ExpectQuery(regexp.QuoteMeta(
        "SELECT * FROM `token` WHERE (`user_id` = ?);",
    )).WithArgs("some-valid-user-id").WillReturnRows(...)
}
```

> 用于测试数据库交互的 Go SQL Mock 驱动。

- 使用 MySQL、PostgreSQL 等数据库时，它适合对预期 SQL 是否被执行进行单元测试。
  - 包路径看起来有点奇怪，但实际使用没有问题。
- 如果你认为“为什么要手写并校验 SQL？”，那就不推荐使用它。

## [golangci/golangci-lint](https://github.com/golangci/golangci-lint) 与 [mvdan/gofumpt](https://github.com/mvdan/gofumpt)

```yaml
# .golangci.yml
linters:
  enable:
    - govet
    - errcheck
    - staticcheck

formatters:
  enable:
    - gofumpt
  settings:
    gofumpt:
      extra-rules: true
```

> golangci-lint：快速的 Go Linter 运行器。gofumpt：比 gofmt 更严格的格式化工具。

- golangci-lint 是 Go 生态事实上的 Linter 运行器。它集成了 100 多个 Linter，并行执行的速度足以满足 CI 使用。
- gofumpt 比 gofmt 更严格，适合在团队内强制统一代码风格。
- 在 golangci-lint 配置中加入 gofumpt，就能在一次执行中完成代码检查和格式校验。

## [failsafe-go/failsafe-go](https://github.com/failsafe-go/failsafe-go)

```go
retryPolicy := retrypolicy.NewBuilder[*http.Response]().
    HandleIf(func(r *http.Response, err error) bool {
        return r != nil && r.StatusCode == http.StatusTooManyRequests
    }).
    WithBackoff(time.Second, 30*time.Second).
    WithMaxRetries(3).
    Build()

resp, err := failsafe.With(retryPolicy).Get(func() (*http.Response, error) {
    return http.Get("https://example.com")
})
```

> 为 Go 提供容错和韧性模式。

- 这是一个容错包，提供了类似 Java resilience4j 的实用模式。
- 可以组合重试、熔断器、限流器、舱壁隔离和自适应节流等多种组件与策略。
- 如果只需要轻量重试，下面的 go-retryablehttp 已经足够；如果需要完整的韧性模式，则更适合使用 failsafe-go。

## [hashicorp/go-retryablehttp](https://github.com/hashicorp/go-retryablehttp)

```go
client := retryablehttp.NewClient()
client.RetryMax = 3

resp, err := client.Get("https://example.com/api")
```

> 可重试的 Go HTTP 客户端。

- 它是在 `net/http` 上增加的一层轻量重试封装。
- 它在基本保留 `http.Client` API 的同时加入了重试逻辑，接入成本很低，值得使用。

## [twmb/franz-go](https://github.com/twmb/franz-go)

```go
// producer
client, _ := kgo.NewClient(kgo.SeedBrokers("localhost:9092"))
defer client.Close()

ctx := context.Background()
client.Produce(
    ctx,
    &kgo.Record{Topic: "my-topic", Value: []byte("hello")},
    nil,
)

// consumer
client, _ := kgo.NewClient(
    kgo.SeedBrokers("localhost:9092"),
    kgo.ConsumeTopics("my-topic"),
    kgo.ConsumerGroup("my-group"),
)
for {
    fetches := client.PollFetches(ctx)
    fetches.EachRecord(func(r *kgo.Record) {
        fmt.Println(string(r.Value))
    })
}
```

> 功能完整的纯 Go Kafka 客户端，支持 Kafka 0.8.0 至 4.1+，涵盖生产、消费、事务和管理等功能。

- 这是一个纯 Go Kafka 包。作者不推荐 [confluent-kafka-go](https://github.com/confluentinc/confluent-kafka-go)，因为它依赖 cgo 环境和 librdkafka，会让构建环境变得麻烦。
- 它的 API 很顺手，附带的插件也确实实用。
- sarama 是长期以来事实上的选择，生态很广；但对于新项目，作者会推荐 franz-go。

## [go-resty/resty](https://github.com/go-resty/resty) 与 [dghubble/sling](https://github.com/dghubble/sling)

```go
// resty
client := resty.New()
resp, err := client.R().
    SetHeader("Accept", "application/json").
    SetResult(&ApiResponse{}).
    Get("https://api.example.com/users/1")

// sling
type Issue struct {
    Title string `json:"title"`
    Body  string `json:"body"`
}
issue := new(Issue)
resp, err := sling.New().Base("https://api.github.com/").
    Path("repos/user/repo/").
    Get("issues/1").
    ReceiveSuccess(issue)
```

> go-resty：用于 Go 的简单 HTTP、REST 和 SSE 客户端。dghubble/sling：用于创建并发送 API 请求的 Go HTTP 客户端。

- 大多数时候只用 `net/http` 就够了，但编写结构化 API 客户端时，这两个包会很有帮助。
- resty：功能丰富，包括链式 API、自动 JSON 编解码和内置重试。
- sling：轻量、可组合的 API 构造器，整体设计更加简洁。

## [go-chi/chi](https://github.com/go-chi/chi)

```go
r := chi.NewRouter()
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)

r.Get("/", func(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("hello"))
})
r.Route("/users", func(r chi.Router) {
    r.Get("/", listUsers)
    r.Post("/", createUser)
    r.Get("/{userID}", getUser)
})

http.ListenAndServe(":3000", r)
```

> 用于构建 Go HTTP 服务的轻量、惯用且可组合的路由器。

- echo 的知名度很高，但 chi 更符合 Go 的惯用风格。它与 `net/http` Handler 完全兼容，而且十分轻量。
- 如果路由数量不多，Go 1.22+ 对 `net/http` 路由能力的增强可能已经足够。参见：[Routing Enhancements for Go 1.22](https://go.dev/blog/routing-enhancements)。
- [不要使用 gin](https://eblog.fly.dev/ginbad.html)。

## 其他推荐

- 需要通过 Slack 发送消息时，使用 [slack-go/slack](https://github.com/slack-go/slack)。
- 需要调用 GitHub API 时，使用 [google/go-github](https://github.com/google/go-github)。
  - 它发布新版本很频繁，记得定期升级。
- 需要接入 Sentry 时，参考官方文档并使用 [getsentry/sentry-go](https://github.com/getsentry/sentry-go)。
  - 默认配置下的错误分组效果不太理想，需要做一些调优作者计划以后另写一篇文章讨论。
- 需要在多个 goroutine 中并发写 map 时，使用 [syncmap](https://pkg.go.dev/golang.org/x/sync/syncmap)。
  - 并发写普通 map 会触发 panic，至少很容易发现；但 slice 并发写失败时不会有同样明显的信号，因此要格外小心。
- 需要处理语义化版本时，使用 [Masterminds/semver](https://github.com/Masterminds/semver)。
- 需要 UUID 时，使用 [google/uuid](https://github.com/google/uuid)。
  - 它也支持 UUID v7。
  - 如果需要更短的 ID，可以考虑 [matoous/go-nanoid](https://github.com/matoous/go-nanoid)。
  - [oklog/ulid](https://github.com/oklog/ulid) 是一种更短、可按时间戳排序的 ID，作者已经在生产环境中使用。UUID v7 同样支持按时间戳排序，但它无法通过双击一次完整选中，略有不便。
- 如果部署到 Kubernetes，使用 [uber-go/automaxprocs](https://github.com/uber-go/automaxprocs) 正确配置 CPU。
  - 否则可能出现 Pod 只分配了 1 个 CPU，`GOMAXPROCS` 却是 32 之类的问题。
- 记录 StatsD 指标时，使用 [smira/go-statsd](https://github.com/smira/go-statsd)。
  - 建议在消费端单独声明接口，并搭配 noop 客户端实现，测试会容易很多。
- 使用 Redis 时，选择 [redis/rueidis](https://github.com/redis/rueidis)。
  - 有人可能不喜欢它的 Builder 模式，但性能很可靠。
  - rueidis 与 [valkey-go](https://github.com/valkey-io/valkey-go) 由同一维护者开发并共享代码库，因此同时支持 Valkey 和 Redis。
  - [redis/go-redis](https://github.com/redis/go-redis) 作为基础选择完全可用，但它在大规模连接 ElastiCache 集群模式时[存在已知问题](https://github.com/redis/go-redis/issues/2046)，因此高流量环境更推荐 rueidis。
  - 编写单元测试时，可以搭配 [alicebob/miniredis](https://github.com/alicebob/miniredis)。
- 集成测试可以考虑 [testcontainers/testcontainers-go](https://github.com/testcontainers/testcontainers-go)。
  - 集成测试的实现方式很多，具体取决于团队环境，但 Testcontainers 是值得纳入候选的可靠方案。
- 需要国际化支持时，可以看看 [biter777/countries](https://github.com/biter777/countries) 和 [nyaruka/phonenumbers](https://github.com/nyaruka/phonenumbers)。
  - countries 处理国家代码、货币和语言等信息；phonenumbers 是 Google libphonenumber 的 Go 移植版。平时不一定用得上，但真正需要国际化时非常有价值。
- 为不依赖 CGO 的 Go 应用构建容器镜像时，可以尝试 [ko-build/ko](https://github.com/ko-build/ko)。
  - 它无需 Dockerfile，就能把 Go 应用构建并推送为 distroless 镜像。需要比 GoReleaser 更轻量的方案时可以考虑。

---

以上就是作者经常使用、也确实觉得实用的一批包。这个列表明显偏向服务端开发，也省略了高度细分的包，例如计算 Levenshtein 距离的工具。如果以后发现其他值得推荐的包，作者会继续补充。

## 其他值得参考的资源

- [mingrammer/go-web-framework-stars](https://github.com/mingrammer/go-web-framework-stars)
- [Which Go router should I use?](https://www.alexedwards.net/blog/which-go-router-should-i-use)
- [Go Libraries/Packages I Like | Ben E. C. Boyter](https://boyter.org/posts/go-libraries-i-like/)
