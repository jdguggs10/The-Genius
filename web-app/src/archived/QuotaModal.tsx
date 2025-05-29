// Archived QuotaModal component for future use
import { motion } from 'framer-motion';

type QuotaModalProps = {
  onClose: () => void;
};

export default function QuotaModal({ onClose }: QuotaModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-lg p-6 max-w-md w-full"
      >
        <h2 className="text-xl font-bold mb-4">Daily Limit Reached</h2>
        <p className="mb-4">
          You've reached your 5 message daily limit for the web version.
        </p>
        <p className="mb-4">
          For unlimited access, download our iOS app!
        </p>
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            Close
          </button>
        </div>
      </motion.div>
    </div>
  );
} 