CREATE TABLE [dbo].[FilecoinDeals](
	[Id] [bigint] IDENTITY(1,1) NOT NULL,
	[MinerId] [nvarchar](16) NOT NULL,
	[DatasetName] [nvarchar](128) NOT NULL,
	[ImportPath] [nvarchar](256) NOT NULL,
	[DownloadPath] [nvarchar](256) NOT NULL,
	[DatasetSupplier] [nvarchar](128) NOT NULL,
	[Filename] [nvarchar](132) NOT NULL,
	[DownloadURL] [nvarchar](512) NULL,
	[DownloadStatus] [nvarchar](16) NULL,
	[PieceCid] [nvarchar](132) NULL,
	[DealId] [nvarchar](132) NULL,
	[DealStatus] [nvarchar](256) NULL
) ON [PRIMARY]
GO
