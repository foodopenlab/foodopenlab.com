import { BraindeadEmailForm } from "@/components/admin/braindead/email-form"

export default function AdminBraindeadEmailPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">BRAINDEAD · AI MAIL</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">메일 보내기</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          내용을 설명하면 Exaone AI가 이메일 본문을 작성하고 n8n을 통해 Gmail로 발송합니다.
        </p>
      </div>
      <BraindeadEmailForm />
    </div>
  )
}
