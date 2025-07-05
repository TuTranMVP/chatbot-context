"""
Download and save Hugging Face MMS TTS model locally
This script downloads the Facebook MMS TTS English model for offline use
"""

import os

from transformers import AutoTokenizer, VitsModel

model_name = 'facebook/mms-tts-eng'
local_dir = './mms-tts-eng-local'


def download_tts_model():
    """Download and save TTS model and tokenizer locally"""
    try:
        print(f'🔄 Starting download of {model_name}...')
        print(f'📁 Saving to: {local_dir}')

        # Create directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)

        # Check if model already exists
        if os.path.exists(os.path.join(local_dir, 'config.json')):
            print('✅ Model already exists locally!')
            return True

        print('📥 Downloading model (this may take a few minutes)...')
        # Download and save model
        model = VitsModel.from_pretrained(model_name)
        model.save_pretrained(local_dir)
        print('✅ Model downloaded and saved!')

        print('📥 Downloading tokenizer...')
        # Download and save tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(local_dir)
        print('✅ Tokenizer downloaded and saved!')

        print(f'🎉 Model and tokenizer successfully saved to: {local_dir}')
        return True

    except Exception as e:
        print(f'❌ Error downloading model: {e}')
        return False


if __name__ == '__main__':
    success = download_tts_model()
    if success:
        print('\n🚀 Ready to use offline TTS!')
    else:
        print('\n💔 Download failed. Check your internet connection.')
