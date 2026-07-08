"use client"

import { Loader2, Mic, Plus, SendHorizontal, SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"
import {
  geminiLandingChatModelTriggerClassName,
  geminiLandingChatToolbarActionsClassName,
  geminiLandingChatToolbarLeftClassName,
  geminiLandingChatToolbarRowClassName,
} from "@/components/landing/gemini-landing-chat-toolbar-layout"
import {
  geminiLandingChatToolbarIconButtonChrome,
  geminiLandingChatToolbarSendReadyChrome,
  geminiLandingChatToolbarVoiceChrome,
} from "@/components/landing/gemini-landing-chat-toolbar-controls"
import { GEMINI_MODEL_FAST, GEMINI_MODEL_LITE } from "@/lib/gemini-models"

export type GeminiLandingChatToolbarProps = {
  chatInstanceId: string
  model: string
  onModelChange: (value: string) => void
  onVoiceClick: () => void
  onSendClick: () => void
  micDisabled: boolean
  sendDisabled: boolean
  loading: boolean
}

export function GeminiLandingChatToolbar({
  chatInstanceId,
  model,
  onModelChange,
  onVoiceClick,
  onSendClick,
  micDisabled,
  sendDisabled,
  loading,
}: GeminiLandingChatToolbarProps) {
  const modelTriggerDomId = `${chatInstanceId}-landing-model`
  const voiceBtnDomId = `${chatInstanceId}-landing-voice`
  const sendBtnDomId = `${chatInstanceId}-landing-send`

  return (
    <div className={geminiLandingChatToolbarRowClassName} data-landing-chat="toolbar">
      <div className={geminiLandingChatToolbarLeftClassName} data-landing-chat="toolbar-left">
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className={`${geminiLandingChatToolbarIconButtonChrome} text-muted-foreground`}
          data-chat-control="attach"
          id={`${chatInstanceId}-landing-attach`}
          disabled
          title="첨부는 곧 지원 예정"
        >
          <Plus className="h-5 w-5" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1.5 rounded-full text-muted-foreground"
          data-chat-control="tools"
          id={`${chatInstanceId}-landing-tools`}
          disabled
          title="준비 중"
        >
          <SlidersHorizontal className="h-4 w-4" />
          <span className="hidden sm:inline">도구</span>
        </Button>
      </div>

      <div className={geminiLandingChatToolbarActionsClassName}>
        <div data-chat-control-zone="model">
          <Select value={model} onValueChange={onModelChange}>
            <SelectTrigger
              id={modelTriggerDomId}
              size="sm"
              data-chat-control="model"
              className={geminiLandingChatModelTriggerClassName}
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={GEMINI_MODEL_FAST}>2.5 Flash-Lite</SelectItem>
              <SelectItem value={GEMINI_MODEL_LITE}>3.1 Flash-Lite</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex shrink-0 items-center gap-1.5" data-chat-control-zone="voice-send">
          <Button
            type="button"
            size="icon"
            variant="ghost"
            id={voiceBtnDomId}
            data-chat-control="voice"
            className={geminiLandingChatToolbarVoiceChrome}
            onClick={onVoiceClick}
            disabled={micDisabled}
            title="음성 입력"
            aria-label="음성 입력"
          >
            <Mic className="h-5 w-5" aria-hidden />
          </Button>

          <Button
            type="button"
            size="icon"
            variant="default"
            id={sendBtnDomId}
            data-chat-control="send"
            className={cn(geminiLandingChatToolbarIconButtonChrome, geminiLandingChatToolbarSendReadyChrome)}
            onClick={onSendClick}
            disabled={sendDisabled}
            title="보내기"
            aria-label="보내기"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <SendHorizontal className="h-4 w-4" aria-hidden />
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
