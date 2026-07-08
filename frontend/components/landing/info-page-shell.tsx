import Link from "next/link"
import { ArrowLeft, Shield } from "lucide-react"
import { Footer } from "@/components/landing/footer"
import { Button } from "@/components/ui/button"

type InfoPageShellProps = {
  title: string
  description?: string
  children: React.ReactNode
}

export function InfoPageShell({ title, description, children }: InfoPageShellProps) {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <main className="flex-1">
        <div className="border-b border-border/60 bg-card/40">
          <div className="container mx-auto flex max-w-3xl flex-col gap-4 px-4 py-8 sm:py-10">
            <Button variant="ghost" size="sm" className="w-fit gap-2 px-0" asChild>
              <Link href="/">
                <ArrowLeft className="size-4" aria-hidden />
                홈으로
              </Link>
            </Button>
            <div className="flex items-start gap-3">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                <Shield className="size-5" aria-hidden />
              </div>
              <div className="min-w-0">
                <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">{title}</h1>
                {description ? (
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
                ) : null}
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto max-w-3xl px-4 py-8 sm:py-10">
          <article className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-p:text-muted-foreground prose-li:text-muted-foreground dark:prose-invert">
            {children}
          </article>
        </div>
      </main>
      <Footer />
    </div>
  )
}
