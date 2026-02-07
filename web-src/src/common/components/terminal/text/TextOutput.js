import {addClass} from '@/common/utils/common'

export class TextOutput {
    constructor() {
        this.element = document.createElement('code')
        addClass(this.element, 'text-output')
    }

    clear() {
        this.element.innerHTML = ''
    }

    write(text) {
        this.element.appendChild(document.createTextNode(text))
    }

    removeInlineImage(outputPath) {
    }

    setInlineImage(outputPath, downloadUrl) {
        // Inline images not supported for text output
    }
}